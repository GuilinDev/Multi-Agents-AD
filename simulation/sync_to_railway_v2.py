"""
Sync local simulation results to Railway — v2 with retry + throttle.
Only syncs events not already on Railway (incremental).
"""
import sqlite3
import httpx
import asyncio
import json

LOCAL_DB = "/home/guilinzhang/allProjects/memowell-ai/api/memowell.db"
RAILWAY_URL = "https://memowell-ai-production.up.railway.app"
THROTTLE = 2.5  # seconds between requests (stay under 30 RPM Groq limit)
MAX_RETRIES = 3


async def sync():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    async with httpx.AsyncClient(base_url=RAILWAY_URL, timeout=60.0) as client:
        # Check how many events Railway already has
        r = await client.get("/api/patients")
        patients = r.json()
        
        # Count existing events on Railway
        railway_event_count = 0
        for p in patients:
            try:
                r2 = await client.get(f"/api/patients/{p['id']}/events")
                if r2.status_code == 200:
                    railway_event_count += len(r2.json())
            except:
                pass
        print(f"Railway already has {railway_event_count} events across {len(patients)} patients")

        # Get local events
        c.execute("SELECT * FROM behavioral_events ORDER BY id")
        all_events = c.fetchall()
        print(f"Local DB has {len(all_events)} events")

        # Skip events already synced (approximate by count)
        events_to_sync = all_events[railway_event_count:]
        print(f"Events to sync: {len(events_to_sync)}")

        if not events_to_sync:
            print("Nothing to sync!")
            conn.close()
            return

        # Build patient name->railway_id map
        patient_map = {p["name"]: p["id"] for p in patients}
        
        # Build local patient id->name map
        c.execute("SELECT id, name FROM patients")
        local_patients = {r["id"]: r["name"] for r in c.fetchall()}

        synced = 0
        errors = 0

        for ev in events_to_sync:
            patient_name = local_patients.get(ev["patient_id"], "")
            railway_pid = patient_map.get(patient_name, ev["patient_id"])

            for attempt in range(MAX_RETRIES):
                try:
                    r = await client.post("/api/events/report", data={
                        "patient_id": railway_pid,
                        "reporter_id": 1,
                        "text": ev["description"] or "No description",
                    })

                    if r.status_code == 200:
                        result = r.json()
                        event_id = result.get("event_id")

                        if ev["intervention_description"] and event_id:
                            await client.post(f"/api/events/{event_id}/intervention", json={
                                "description": ev["intervention_description"],
                            })

                        if ev["outcome_description"] and event_id:
                            await client.post(f"/api/events/{event_id}/outcome", json={
                                "description": ev["outcome_description"],
                                "resolved": bool(ev["resolved"]),
                            })

                        synced += 1
                        break
                    elif r.status_code in (429, 500, 502, 503):
                        wait = THROTTLE * (attempt + 2)
                        print(f"  ⚠️ {r.status_code}, retry {attempt+1}, wait {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        errors += 1
                        if errors <= 5:
                            print(f"  ❌ Event {ev['id']}: {r.status_code}")
                        break
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(THROTTLE * 2)
                    else:
                        errors += 1
                        if errors <= 5:
                            print(f"  ❌ Event {ev['id']}: {e}")

            if synced % 10 == 0 and synced > 0:
                print(f"  ... {synced}/{len(events_to_sync)} synced")

            await asyncio.sleep(THROTTLE)

        print(f"\n✅ Synced: {synced}/{len(events_to_sync)} ({errors} errors)")

    conn.close()

if __name__ == "__main__":
    asyncio.run(sync())
