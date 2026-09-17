# RelationshipOS implementation status

## Implemented in code
- Mobile PWA shell and voice transcript ingestion
- People, contexts, interactions, reminders, candidate facts and confirmed facts
- OpenAI-compatible AI extraction seam
- Source/provenance records
- Relationship priority scoring and Today queue
- Email/phone/fuzzy-name identity resolution
- Natural-language CRM intents: stale contacts, commitments, company contacts, search
- Person and meeting briefing engine
- Local hybrid lexical search (semantic vector backend remains optional)
- Relationship graph and introduction candidates
- Life-event detection
- LinkedIn Connections CSV importer
- WhatsApp text-export parser
- Gmail read-only collector and Google OAuth helper
- Google Calendar read-only collector
- Telegram notification adapter
- MCP tools for CRM queries and person context
- Docker/Docker Compose self-hosting
- Acceptance/unit tests for core deterministic logic

## Requires operator credentials/data before live acceptance
These paths are implemented but cannot be truthfully marked live-tested until credentials or exports are supplied:
- Gmail OAuth and real mailbox sync
- Calendar OAuth and real event sync
- Telegram delivery
- LLM extraction against the selected local/cloud model
- LinkedIn import against the user's export
- WhatsApp import against the user's export

## Platform constraints
LinkedIn personal-message synchronization is not treated as an unrestricted API integration; Connections export/import is the supported baseline. WhatsApp personal history uses export/import; official Business API support can be added separately.

## Acceptance definition
A feature is `live verified` only after it runs against the configured external account/data and the resulting CRM records are inspected. Code presence alone is not live verification.
