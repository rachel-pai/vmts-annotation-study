#!/usr/bin/env python3
"""Build 30 twelve-item batches: 72 items receive five ratings each."""
from collections import Counter
import json, random
from pathlib import Path
ROOT=Path(__file__).parent
items=sorted(x["item_id"] for x in json.loads((ROOT/"data/tasks.json").read_text()))
if len(items)!=72: raise ValueError("Expected 72 items")
batches={}; n=1
for wave in range(5):
    shuffled=items[:]; random.Random(20260715+wave).shuffle(shuffled)
    for start in range(0,72,12): batches[f"P{n}"]=shuffled[start:start+12]; n+=1
counts=Counter(x for b in batches.values() for x in b)
assert len(batches)==30 and set(map(len,batches.values()))=={12} and set(counts.values())=={5}
(ROOT/"data/prolific-batches.json").write_text(json.dumps(batches,indent=2)+"\n")
(ROOT/"data/design-summary.json").write_text(json.dumps({
    "items":72,
    "ratings_per_item":5,
    "participant_slots":30,
    "items_per_participant":12,
    "total_judgments":360,
    "assignment_seed_base":20260715,
},indent=2)+"\n")
batch_checks="\n        || ".join(f"(batchId == '{b}' && itemId in {json.dumps(v,separators=(',',':'))})" for b,v in batches.items())
rules=(ROOT/"firestore.rules").read_text()
import re
rules=re.sub(r"function validBatch\(batchId\) \{.*?\n    \}",f"function validBatch(batchId) {{\n      return batchId in {json.dumps(list(batches),separators=(',',':'))};\n    }}",rules,count=1,flags=re.S)
rules=re.sub(r"function validItem\(batchId, itemId\) \{.*?\n    \}",f"function validItem(batchId, itemId) {{\n      return {batch_checks};\n    }}",rules,count=1,flags=re.S)
rules=rules.replace("completedItems <= 18","completedItems <= 12")
(ROOT/"firestore.rules").write_text(rules)
print("Built 30 batches × 12 items; exactly 5 ratings/item")
