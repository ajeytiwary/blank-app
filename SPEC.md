# RelationshipOS product + engineering spec

## Product principle
RelationshipOS is a private relationship memory, not a sales CRM. One canonical Person can participate in several contexts (personal, business, MeasureNature, Saha, etc.) without duplicating identity.

## V0.1 — implemented foundation
- FastAPI API + SQLite local store
- installable mobile PWA shell
- people, interactions, facts and reminders schema
- Today endpoint prioritizing stale relationships
- browser voice transcription seam
- personal/business context on a person
- offline shell via service worker

## V0.2 — relationship intelligence
1. LLM adapter supporting any OpenAI-compatible endpoint, including local models.
2. Voice/text extraction into candidate facts, events, commitments and reminders.
3. Confirmation queue: sensitive or ambiguous facts are never silently promoted to durable memory.
4. Relationship score: recency, frequency, importance, reciprocity, open-loop urgency and upcoming life events. Scores explain their components.
5. Contact briefing: identity, role/company, last contact, recent topics, important facts, life events, open loops and suggested next action.
6. Natural-language query endpoint: “Who should I contact?”, “What did we last discuss?”, “Who can introduce me to X?”

## V0.3 — ingestion
- Gmail OAuth: threads, participants, timestamps; start read-only.
- Google Calendar OAuth: attendees and meetings.
- LinkedIn official data export CSV import; do not depend on brittle scraping.
- Telegram bot as capture/query surface.
- WhatsApp adapter isolated behind a connector interface so it can be replaced as access methods change.
- CSV/vCard import.

## Identity resolution
Raw observations are SourceIdentity records. Canonical Person records merge identities using deterministic email/phone matches first, then explicit user-confirmed fuzzy matches. Never auto-merge low-confidence identities.

## Memory policy
Each extracted fact carries source, timestamp, confidence, sensitivity and confirmation state. Users can correct/delete durable facts. AI-generated inferences must not be stored as facts without evidence.

## Mobile/voice
PWA is the default phone surface. Voice pipeline: speech -> transcript -> intent/extraction -> confirmation -> write -> optional reminder. Browser SpeechRecognition is only the MVP; production uses a server STT adapter (Whisper/faster-whisper) for cross-browser consistency.

## Integration strategy
LifeOS is the architectural reference for local-first aggregation, entity resolution, hybrid search, voice and Google connectors. PingCRM is the reference for relationship scoring, life-event detection and contextual follow-ups. Avoid direct code copying unless license compatibility and attribution are reviewed; implement clean interfaces around the desired concepts.

## Deployment target
Docker Compose on an Ubuntu host, HTTPS via Caddy, accessed from phone as an installed PWA. Database migrates from SQLite to PostgreSQL when Gmail/Calendar backfills and multi-worker jobs are enabled.

## Security
- OAuth tokens encrypted at rest before production connectors are enabled.
- secrets only via environment/secret store, never Git.
- read-only scopes first.
- explicit confirmation before sending messages or changing external systems.
- audit log for agent actions.
- authentication required before exposing beyond LAN/Tailscale.

## Definition of useful V1
From a phone, user can dictate a meeting note, resolve it to a person, review extracted facts/open loops, set a reminder, see a morning relationship brief, search prior interactions, and receive a useful pre-meeting briefing sourced from Gmail + Calendar + manual/voice notes.
