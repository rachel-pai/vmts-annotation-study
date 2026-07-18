#!/usr/bin/env python3
"""Fail-fast audit for the static Prolific study."""
from __future__ import annotations
import argparse, collections, json, re
from pathlib import Path

ROOT=Path(__file__).parent

def main():
    p=argparse.ArgumentParser(); p.add_argument("--require-live",action="store_true"); a=p.parse_args()
    tasks=json.loads((ROOT/"data/tasks.json").read_text()); batches=json.loads((ROOT/"data/prolific-batches.json").read_text())
    ids=[x["item_id"] for x in tasks]; counts=collections.Counter(x for batch in batches.values() for x in batch)
    assert len(tasks)==72 and len(ids)==len(set(ids)),"Need 72 unique tasks"
    assert len(batches)==30 and set(map(len,batches.values()))=={12},"Need 30 batches of 12"
    assert set(counts)==set(ids) and set(counts.values())=={5},"Every item must receive exactly five ratings"
    required={"item_id","topic","before","now","action","saved_note"}
    assert all(required==set(x) and all(str(x[k]).strip() for k in required) for x in tasks),"Task schema/empty text error"
    cfg=(ROOT/"study-config.js").read_text()
    locked="CONFIGURE_" in cfg or 'status: "APPROVED"' not in cfg
    assert "contactName" not in cfg,"Participant configuration must not contain a researcher name"
    assert all(token in (ROOT/"app.js").read_text() for token in ("PROLIFIC_PID","STUDY_ID","SESSION_ID","consentVersion"))
    assert all(f'"P{i}"' in (ROOT/"firestore.rules").read_text() for i in range(1,31))
    if a.require_live and locked: raise SystemExit("LOCKED: fill approved ethics, payment, completion code, and set status APPROVED")
    print(json.dumps({"status":"PASS","production_locked":locked,"tasks":72,"participant_slots":30,"items_each":12,"ratings_each":5,"judgments":360},indent=2))
if __name__=="__main__": main()
