#!/usr/bin/env python3
"""Build 24 fifteen-item batches: 72 items receive five ratings each."""
from collections import Counter
import json, random
from pathlib import Path
ROOT=Path(__file__).parent
items=sorted(x["item_id"] for x in json.loads((ROOT/"data/tasks.json").read_text()))
if len(items)!=72: raise ValueError("Expected 72 items")
groups=json.loads((ROOT/"data/task-groups.json").read_text())
by_case={}
for item in items: by_case.setdefault(groups[item],[]).append(item)
cases=sorted(by_case); random.Random(20260718).shuffle(cases)
for case in cases: random.Random(f"20260718|{case}").shuffle(by_case[case])
assert len(cases)==24 and set(map(len,by_case.values()))=={3}
batches={f"P{b+1}":[] for b in range(24)}
for wave in range(5):
    for b in range(24):
        for variant in range(3):
            case=cases[(b+8*variant+3*wave)%24]
            batches[f"P{b+1}"].append(by_case[case][variant])
counts=Counter(x for b in batches.values() for x in b)
assert len(batches)==24 and set(map(len,batches.values()))=={15} and set(counts.values())=={5}
assert all(len(v)==len(set(v)) for v in batches.values())
assert all(len({groups[x] for x in v})==15 for v in batches.values())
(ROOT/"data/prolific-batches.json").write_text(json.dumps(batches,indent=2)+"\n")
(ROOT/"data/design-summary.json").write_text(json.dumps({
    "items":72,
    "ratings_per_item":5,
    "participant_slots":24,
    "items_per_participant":15,
    "total_judgments":360,
    "assignment_seed":20260718,
},indent=2)+"\n")
batch_checks="\n        || ".join(f"(batchId == '{b}' && itemId in {json.dumps(v,separators=(',',':'))})" for b,v in batches.items())
rules=(ROOT/"firestore.rules").read_text()
import re
rules=re.sub(r"function validBatch\(batchId\) \{.*?\n    \}",f"function validBatch(batchId) {{\n      return batchId in {json.dumps(list(batches),separators=(',',':'))};\n    }}",rules,count=1,flags=re.S)
rules=re.sub(r"function validItem\(batchId, itemId\) \{.*?\n    \}",f"function validItem(batchId, itemId) {{\n      return {batch_checks};\n    }}",rules,count=1,flags=re.S)
rules=re.sub(r"completedItems <= \d+","completedItems <= 15",rules)
(ROOT/"firestore.rules").write_text(rules)
print("Built 24 batches × 15 items; exactly 5 ratings/item")
