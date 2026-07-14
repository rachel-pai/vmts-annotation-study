# Prolific-ready VMTS annotation study

Static GitHub Pages front end with Firebase Anonymous Authentication and Cloud
Firestore. Everyone uses one study URL; Prolific supplies participant parameters,
and the site transactionally assigns one of six balanced 15/16-item batches.
Items with any source truncation are excluded: 31 complete items remain, with
exactly three independent ratings per item.

## What participants see

1. Ethics approval, researcher contact, duration, payment, risks, data handling,
   withdrawal wording, and three explicit consent confirmations on the homepage.
2. Prolific link validation and automatic stable batch assignment.
3. A worked example, plain-language labels, and 15 or 16 annotation items.
4. A configured Prolific completion code and return button.

Recruit participants who are comfortable reading software instructions and
short code snippets; this is not a general-population language task.

Raw `PROLIFIC_PID`, `STUDY_ID`, and `SESSION_ID` values are never written to
Firestore. The browser stores only SHA-256-derived participant/study/session keys.
These remain pseudonymous research data and must still be handled accordingly.

## Required configuration before recruitment

1. Fill every `CONFIGURE_*` value in `study-config.js` using the exact approved
   ethics documents and Prolific listing. Set `ethics.status` to `APPROVED` only
   after approval. The page deliberately blocks participation until this is done.
2. Create/register a Firebase web app, enable Anonymous Authentication, create
   Firestore, and put the public web configuration in `firebase-config.js`.
3. Deploy `firestore.rules`. The public client cannot read submitted responses;
   claims are created atomically, and writes are limited to the participant's batch.
4. In Firebase Authentication, authorize the final `*.github.io` domain.
5. Deploy through `.github/workflows/pages.yml` (Pages source: GitHub Actions).

If assignments change, run:

```bash
python3 annotation-site/build_prolific_design.py
```

This rebuilds `data/prolific-batches.json` and the matching rule allowlists. It
fails unless all 31 non-truncated items receive exactly three ratings.

## Prolific URL

Give Prolific the single GitHub Pages study URL with its standard placeholders:

```text
https://YOUR_ACCOUNT.github.io/YOUR_REPOSITORY/?PROLIFIC_PID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
```

Set the same completion code in Prolific and `study-config.js`. Recruit exactly
6 completed participants for the current fixed design. Use Prolific replacement
recruitment for returned/timed-out submissions; a claimed but abandoned batch must
be released administratively before a replacement can receive it.

## Local preview

```bash
python3 -m http.server 8765 --directory annotation-site
```

The production lock remains active locally until real study configuration is
present. Do not insert invented ethics details just to bypass it.

## Export

Export the `responses` collection from an authorized Firebase administrative
environment. The website intentionally cannot read submitted annotations.
