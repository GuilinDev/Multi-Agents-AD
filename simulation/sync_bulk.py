#!/usr/bin/env python3
"""
Bulk sync local simulation data to Railway — NO LLM calls.
Reads local SQLite, packages patients + events, POST to /api/events/bulk-import.
"""

import sqlite3
import json
import sys
import requests

LOCAL_DB = "/home/guilinzhang/allProjects/memowell-ai/api/memowell.db"
RAILWAY_URL = "https://memowell-ai-production.up.railway.app"

def load_local_data():
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load patients
    c.execute("SELECT * FROM patients")
    patients = []
    for row in c.fetchall():
        patients.append({
            "name": row["name"],
            "room": row["room"] or "",
            "diagnosis": row["diagnosis"] or "",
            "cognitive_level": row["cognitive_level"] or "",
            "medications": json.loads(row["medications"]) if row["medications"] else [],
            "special_notes": row["special_notes"] or "",
        })

    # Load events with patient names
    c.execute("""
        SELECT e.*, p.name as patient_name 
        FROM behavioral_events e 
        JOIN patients p ON e.patient_id = p.id
        ORDER BY e.event_at
    """)
    events = []
    for row in c.fetchall():
        protocol = row["protocol_matched"]
        if protocol:
            try:
                protocol = json.loads(protocol)
            except:
                protocol = []
        else:
            protocol = []

        events.append({
            "patient_name": row["patient_name"],
            "reporter_name": "Simulation Agent",
            "shift": row["shift"] or "Day",
            "event_type": row["event_type"] or "Other",
            "severity": row["severity"] or "Medium",
            "description": row["description"] or "",
            "location": row["location"] or "",
            "trigger": row["trigger"] or "",
            "protocol_matched": protocol,
            "intervention_description": row["intervention_description"] or "",
            "outcome_description": row["outcome_description"] or "",
            "resolved": bool(row["resolved"]),
            "event_at": row["event_at"],
        })

    conn.close()
    return patients, events


def sync():
    print(f"Loading local data from {LOCAL_DB}...")
    patients, events = load_local_data()
    print(f"  Found {len(patients)} patients, {len(events)} events")

    # Send in batches (Railway may have request size limits)
    BATCH_SIZE = 50
    total_imported = 0

    # First batch: all patients + first batch of events
    for i in range(0, len(events), BATCH_SIZE):
        batch_events = events[i:i+BATCH_SIZE]
        payload = {
            "patients": patients if i == 0 else [],  # Only send patients in first batch
            "events": batch_events,
        }

        print(f"  Sending batch {i//BATCH_SIZE + 1} ({len(batch_events)} events)...")
        try:
            resp = requests.post(
                f"{RAILWAY_URL}/api/events/bulk-import",
                json=payload,
                timeout=60,
            )
            if resp.status_code == 200:
                result = resp.json()
                total_imported += result.get("events_imported", 0)
                print(f"    ✅ {result}")
            else:
                print(f"    ❌ HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"    ❌ Error: {e}")

    print(f"\nDone! Total imported: {total_imported}/{len(events)}")

    # Verify via stats endpoint
    try:
        stats = requests.get(f"{RAILWAY_URL}/api/events/stats/dashboard", timeout=30)
        if stats.status_code == 200:
            d = stats.json()
            print(f"\nRailway Dashboard Stats:")
            print(f"  Events: {d['total_events']}")
            print(f"  Patients: {d['total_patients']}")
            print(f"  Protocol coverage: {d['protocol_coverage_pct']}%")
            print(f"  Intervention rate: {d['intervention_rate_pct']}%")
            print(f"  Resolution rate: {d['resolution_rate_pct']}%")
    except:
        pass


if __name__ == "__main__":
    sync()
