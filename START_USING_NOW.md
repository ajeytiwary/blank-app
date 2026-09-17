# RelationshipOS — Start Using It Now

This guide gets the current local-first build running without Google, Telegram, LinkedIn API, or any other OAuth credentials.

## 1. Get the branch

```bash
git clone https://github.com/ajeytiwary/blank-app.git relationship-os
cd relationship-os
git checkout relationship-os-v0.2
```

## 2. Run it locally

### Fastest: Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` on the computer.

### Docker

```bash
docker compose up --build
```

Then open `http://localhost:8000`.

## 3. Prove the workflow with demo data

On the Today screen press **Load demo data**. This deliberately replaces the current local database, so use it before adding real contacts.

The demo exercises the same downstream CRM pipeline intended for live integrations: people, interactions, source records, reminders, life events, identity matching, relationship priority, queries and meeting context.

Try the Ask tab:

- `Who haven't I spoken to?`
- `What did I promise?`
- `Who do I know at Acme?`

Check Today for relationship priorities and open loops. Check Inbox for extracted facts waiting for confirmation.

## 4. Start using it with real information today

Add important people under **People**. Use contexts to keep the same CRM useful across `personal`, `business`, `MeasureNature`, and `Saha` relationships.

After a call, coffee, meeting, WhatsApp conversation or networking event, go to **Today**, select the person and type a short natural-language note such as:

> Met Maya after the biodiversity event. She is interested in a ForestPulse pilot. Her birthday is 12 October. I promised to send the one-page proposal Friday.

Press **Save + extract**. RelationshipOS stores the source note and interaction and passes it through the configured extraction layer. Review uncertain/sensitive extracted memories in **Inbox** before trusting them.

The most useful daily habit is simple:

1. Morning: open **Today** and look at people-to-contact + open loops.
2. Immediately after meaningful conversations: capture a 10–30 second note.
3. Before contacting someone: search/ask for their context and open commitments.
4. Once a week: inspect stale contacts and reconnect intentionally.

## 5. Voice on your phone

The UI is a PWA and includes browser speech recognition when the browser exposes `SpeechRecognition`/`webkitSpeechRecognition`. On supported browsers tap the microphone, speak, check the transcript, select the person, then press **Save + extract**.

For reliable phone access from your home server, expose port 8000 only over a private network such as Tailscale or put the application behind HTTPS + authentication. Do not expose the current unauthenticated development server directly to the public internet because it contains personal relationship data.

Once served over HTTPS, use the browser's **Add to Home Screen / Install app** function to make it behave like an app.

## 6. Optional AI — local or hosted OpenAI-compatible endpoint

Without an LLM, RelationshipOS uses a conservative fallback and does not invent facts. To enable structured AI extraction, configure an OpenAI-compatible `/v1` endpoint:

```bash
export RELATIONSHIPOS_LLM_URL=http://localhost:11434/v1
export RELATIONSHIPOS_LLM_MODEL=YOUR_MODEL
export RELATIONSHIPOS_LLM_API_KEY=
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

For Ollama running outside Docker, `http://localhost:11434/v1` is the usual local endpoint. When the app itself runs in Docker, use a hostname reachable from the container (commonly `host.docker.internal` where supported) instead of blindly using localhost.

A hosted OpenAI-compatible provider works the same way: set the provider's base `/v1` URL, model and API key. Keep keys in environment variables, never in Git.

## 7. Imports available before OAuth

The backend already exposes import endpoints for LinkedIn CSV and WhatsApp text exports. These are deliberately file-import based because they let you bootstrap relationship history without granting a third-party API permanent access.

- `POST /api/import/linkedin` — multipart upload of a LinkedIn connections CSV.
- `POST /api/import/whatsapp` — multipart upload of an exported WhatsApp `.txt` conversation.

The current WhatsApp endpoint parses the export for inspection; do not assume every parsed message has been committed to the CRM until the import response/workflow explicitly says so.

## 8. API and debugging

FastAPI automatically exposes interactive API documentation at `http://localhost:8000/docs`.

Useful endpoints include:

```text
GET  /api/health
GET  /api/today
GET  /api/people
POST /api/people
POST /api/ingest
POST /api/query
GET  /api/inbox
GET  /api/search?q=...
POST /api/meeting-brief
GET  /api/graph
POST /api/demo/reset-and-seed
```

Run tests with:

```bash
pytest -q
```

## 9. Back up your data

The default development database is the SQLite file `relationshipos.db` in the repository root. Stop the application before taking a simple file-level backup:

```bash
cp relationshipos.db relationshipos-backup-$(date +%F).db
```

Set `RELATIONSHIPOS_DB` if you want the database somewhere outside the Git checkout, for example a persistent private data directory.

## 10. When you are ready for Google OAuth

Do not change the CRM workflow. OAuth should only replace the mock/manual source adapters. The intended live path is:

```text
Gmail / Calendar
      ↓
source entity + provenance
      ↓
identity resolution
      ↓
canonical person
      ↓
interaction / meeting
      ↓
AI extraction
      ↓
confirmation inbox
      ↓
facts + commitments + life events
      ↓
Today / Ask / briefing
```

Start with read-only Gmail and Calendar scopes. Keep OAuth refresh tokens out of Git. After credentials are configured, first run against a small date range/account and inspect resolved identities before importing a large mailbox history.

## Current security boundary

This is currently a self-hosted single-user application. It is appropriate for local/private-network experimentation. It is **not** yet appropriate to expose directly to the public internet: application authentication, hardened authorization, encrypted-at-rest OAuth token storage, rate limiting and production deployment controls need to be in place first.
