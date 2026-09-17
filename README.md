# RelationshipOS

A mobile-first, voice-ready, self-hosted personal + business relationship CRM.

RelationshipOS is designed to answer questions such as:

- Who should I contact today?
- When did I last speak with someone and what did we discuss?
- What promises or follow-ups are still open?
- What should I remember before my next meeting?
- Which important relationships are going cold?

## What works in the current MVP

- installable mobile PWA shell
- browser voice capture on supported browsers
- FastAPI backend
- local SQLite relationship store
- people with personal/business contexts
- interaction timeline API
- reminders/open loops
- candidate facts schema
- Today view that surfaces stale contacts
- offline app-shell caching

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`. On another device on the same LAN, use the host machine's LAN IP. Voice/PWA capabilities are more reliable behind HTTPS; production deployment should use Caddy or another TLS reverse proxy.

## API

FastAPI docs are available at `/docs`.

Core endpoints:

- `GET /api/today`
- `GET/POST /api/people`
- `GET /api/people/{id}`
- `POST /api/interactions`
- `POST /api/reminders`
- `POST /api/voice-note`

## Next build

See `SPEC.md`. The next slice is the AI extraction/confirmation pipeline followed by Gmail + Google Calendar OAuth ingestion, relationship scoring, pre-meeting briefs and Telegram capture.

## Upstream architectural references

- LifeOS — local-first personal data aggregation, entity resolution, search, voice and Google integrations: https://github.com/nbramia/LifeOS
- PingCRM — relationship scoring, multi-channel timeline, life-event detection and contextual follow-ups: https://github.com/sneg55/pingcrm

The current code is an independent MVP implementation; upstream projects are references rather than vendored dependencies.
