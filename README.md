# Six-annotator VMTS study site

Static GitHub Pages site with Firebase Anonymous Authentication and Cloud
Firestore writes. Each of 72 items is rated by exactly three of six annotators;
each annotator receives 36 items.

## Study flow

1. Intro, consent, and time/privacy explanation. The A--F assignment is read
   from the researcher's personal URL.
2. Label definitions and the decision-vs-write warning.
3. One item per page with progress, required-field validation, back navigation,
   local resume, and Firebase save status.
4. Completion code and participant-side JSON backup.

Policy names, model names, executable labels, and other annotators' responses
are never shown.

## Firebase setup

1. Create/register a Firebase web app and enable Anonymous Authentication.
2. Create a Cloud Firestore database.
3. Copy the web configuration object into `firebase-config.js`.
4. Publish `firestore.rules` using Firebase Console or Firebase CLI. The A--F
   assignment allowlists are compiled directly into the rules, so no public
   configuration document is required.

The rules deny all response reads and deletes. The first anonymous Firebase UID
to open an A--F link claims that slot. Later writes require the same UID and an
item assigned to that slot. Updates retain the original UID, annotator, and
item.

## Local preview

```bash
python3 -m http.server 8765 --directory annotation-site
```

Open `http://127.0.0.1:8765/?annotator=A` (or B--F).

## GitHub Pages

The workflow `.github/workflows/pages.yml` deploys `annotation-site/` whenever
site files change on `main`. In GitHub repository settings, set Pages source to
**GitHub Actions**. Firebase Authentication must also allow the final
`*.github.io` domain.

Distribute six distinct links ending in `?annotator=A` through
`?annotator=F`. Each person should use one browser profile throughout the
study, because anonymous Firebase identity is persisted in that browser.

## Export for analysis

The researcher exports the `responses` collection from Firebase using an
authorized administrative environment. The public website intentionally has
no permission to read submitted labels.
