#!/usr/bin/env python3
"""Build 12 Prolific batches and matching Firestore item allowlists."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).parent
assignments = json.loads((ROOT / "data/assignments.json").read_text())
batches = {}
for annotator, items in assignments.items():
    if len(items) != 36:
        raise ValueError(f"{annotator} has {len(items)} items, expected 36")
    batches[f"{annotator}1"] = items[:18]
    batches[f"{annotator}2"] = items[18:]

counts = Counter(item for items in batches.values() for item in items)
if len(counts) != 72 or set(counts.values()) != {3}:
    raise ValueError("Design must contain 72 items with exactly 3 ratings each")

(ROOT / "data/prolific-batches.json").write_text(
    json.dumps(batches, indent=2) + "\n"
)

batch_checks = "\n        || ".join(
    f"(batchId == '{batch}' && itemId in {json.dumps(items, separators=(',', ':'))})"
    for batch, items in batches.items()
)
rules = f"""rules_version = '2';
service cloud.firestore {{
  match /databases/{{database}}/documents {{
    function validBatch(batchId) {{
      return batchId in {json.dumps(list(batches), separators=(',', ':'))};
    }}
    function validItem(batchId, itemId) {{
      return {batch_checks};
    }}
    function validResponse(r) {{
      return r.keys().hasOnly(['participantKey','batchId','studyKey','sessionKey','itemId','uid','submitted',
        'revision_relation_label','action_consistency_label','write_consistency_label',
        'mixed_validity_preservation_label','confidence_1_to_5','notes','clientUpdatedAt','serverUpdatedAt'])
        && r.participantKey is string && r.participantKey.size() == 64
        && r.studyKey is string && r.studyKey.size() == 64
        && r.sessionKey is string && r.sessionKey.size() == 64
        && validBatch(r.batchId) && validItem(r.batchId, r.itemId)
        && r.revision_relation_label in ['replace','narrow','expand','exception','cancel','reschedule','clarify','unclear']
        && r.action_consistency_label in ['current','legacy','mixed','abstention','unclear']
        && r.write_consistency_label in ['current','legacy','mixed','empty','unclear']
        && r.mixed_validity_preservation_label in ['preserved','corrupted_or_omitted','not_applicable','unclear']
        && r.confidence_1_to_5 in ['1','2','3','4','5']
        && r.notes is string && r.notes.size() <= 500;
    }}
    match /batchClaims/{{batchId}} {{
      allow get: if request.auth != null;
      allow list, update, delete: if false;
      allow create: if request.auth != null && validBatch(batchId)
        && request.resource.data.keys().hasOnly(['participantKey','batchId','uid','studyKey','sessionKey','assignedAt'])
        && request.resource.data.batchId == batchId
        && request.resource.data.uid == request.auth.uid
        && request.resource.data.participantKey is string && request.resource.data.participantKey.size() == 64;
    }}
    match /participants/{{participantKey}} {{
      // A get on a not-yet-created deterministic participant document must be
      // permitted for transactional allocation. Listing remains forbidden.
      allow get: if request.auth != null;
      allow list, delete: if false;
      allow create: if request.auth != null
        && request.resource.data.keys().hasOnly(['participantKey','batchId','uid','studyKey','sessionKey','assignedAt'])
        && request.resource.data.participantKey == participantKey
        && request.resource.data.uid == request.auth.uid && validBatch(request.resource.data.batchId)
        && getAfter(/databases/$(database)/documents/batchClaims/$(request.resource.data.batchId)).data.participantKey == participantKey;
      allow update: if request.auth != null && resource.data.uid == request.auth.uid
        && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['completedAt','completedItems'])
        && request.resource.data.completedItems is int && request.resource.data.completedItems >= 0 && request.resource.data.completedItems <= 18;
    }}
    match /responses/{{responseId}} {{
      allow read, delete: if false;
      allow create: if request.auth != null
        && request.resource.data.uid == request.auth.uid
        && responseId == request.resource.data.participantKey + '_' + request.resource.data.itemId
        && get(/databases/$(database)/documents/participants/$(request.resource.data.participantKey)).data.uid == request.auth.uid
        && get(/databases/$(database)/documents/participants/$(request.resource.data.participantKey)).data.batchId == request.resource.data.batchId
        && validResponse(request.resource.data);
      allow update: if request.auth != null && resource.data.uid == request.auth.uid
        && request.resource.data.uid == resource.data.uid
        && request.resource.data.participantKey == resource.data.participantKey
        && request.resource.data.batchId == resource.data.batchId
        && request.resource.data.itemId == resource.data.itemId
        && get(/databases/$(database)/documents/participants/$(request.resource.data.participantKey)).data.uid == request.auth.uid
        && validResponse(request.resource.data);
    }}
  }}
}}
"""
(ROOT / "firestore.rules").write_text(rules)
print(f"Built {len(batches)} batches; {len(counts)} items; 3 ratings/item")
