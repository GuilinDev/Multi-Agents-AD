"""
Sync local simulation results to Railway deployment.
Pushes patients + events via the CareLoop API.
"""
import sqlite3
import httpx
import asyncio
import json
import sys

LOCAL_DB = "/home/guilinzhang/allProjects/memowell-ai/api/memowell.db"
RAILWAY_URL = "https://memowell-ai-production.up.railway.app"


async def sync():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    async with httpx.AsyncClient(base_url=RAILWAY_URL, timeout=30.0) as client:
        # 1. Check Railway health
        r = await client.get("/api/health")
        print(f"Railway: {r.json()}")

        # 2. Get existing Railway patients
        r = await client.get("/api/patients")
        existing = {p["name"]: p["id"] for p in r.json()}
        print(f"Existing Railway patients: {len(existing)}")

        # 3. Create missing patients
        c.execute("SELECT * FROM patients WHERE id >= 5")
        local_patients = c.fetchall()
        patient_id_map = {}  # local_id -> railway_id

        for p in local_patients:
            if p["name"] in existing:
                patient_id_map[p["id"]] = existing[p["name"]]
                print(f"  ⏭️  {p['name']} exists (railway_id={existing[p['name']]})")
            else:
                try:
                    r = await client.post("/api/patients", json={
                        "facility_id": 1,
                        "name": p["name"],
                        "room": p["room"] or f"Room {p['id']}",
                        "diagnosis": p["diagnosis"] or "Dementia",
                        "cognitive_level": p["cognitive_level"] or "moderate",
                        "medications": json.loads(p["medications"]) if p["medications"] else [],
                        "allergies": [],
                        "special_notes": p["special_notes"] or "",
                    })
                    if r.status_code in (200, 201):
                        data = r.json()
                        patient_id_map[p["id"]] = data["id"]
                        print(f"  ✅ Created {p['name']} (railway_id={data['id']})")
                    else:
                        print(f"  ❌ Failed {p['name']}: {r.status_code}")
                except Exception as e:
                    print(f"  ❌ Error {p['name']}: {e}")

        print(f"\nPatient map: {len(patient_id_map)} mapped")

        # 4. Push events via the report endpoint
        c.execute("""SELECT * FROM behavioral_events ORDER BY id""")
        events = c.fetchall()
        print(f"\nSyncing {len(events)} events...")

        synced = 0
        errors = 0
        for i, ev in enumerate(events):
            local_patient_id = ev["patient_id"]
            railway_patient_id = patient_id_map.get(local_patient_id, local_patient_id)

            try:
                # Report event via form data (matching the API endpoint)
                r = await client.post("/api/events/report", data={
                    "patient_id": railway_patient_id,
                    "reporter_id": 1,
                    "text": ev["description"] or "No description",
                })

                if r.status_code == 200:
                    result = r.json()
                    event_id = result.get("event_id")

                    # Add intervention if exists
                    if ev["intervention_description"] and event_id:
                        await client.post(f"/api/events/{event_id}/intervention", json={
                            "description": ev["intervention_description"],
                        })

                    # Add outcome if exists
                    if ev["outcome_description"] and event_id:
                        await client.post(f"/api/events/{event_id}/outcome", json={
                            "description": ev["outcome_description"],
                            "resolved": bool(ev["resolved"]),
                        })

                    synced += 1
                    if synced % 20 == 0:
                        print(f"  ... {synced}/{len(events)} synced")
                else:
                    errors += 1
                    if errors <= 3:
                        print(f"  ❌ Event {ev['id']}: {r.status_code} {r.text[:100]}")

                # Throttle to avoid overwhelming Railway
                await asyncio.sleep(0.5)

            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  ❌ Event {ev['id']}: {e}")

        print(f"\n✅ Synced: {synced}/{len(events)} events ({errors} errors)")

    conn.close()


if __name__ == "__main__":
    asyncio.run(sync())
