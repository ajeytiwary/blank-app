import sqlite3
from app.services.mock_pipeline import seed_and_run, SCHEMA
from app.services.identity import resolve_person
from app.services.briefing import person_brief

def con():
    c=sqlite3.connect(':memory:'); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c

def test_mock_pipeline_end_to_end():
    c=con(); r=seed_and_run(c)
    assert r['ok'] is True
    assert r['seeded_people'] >= 5
    assert r['linkedin']['matched'] >= 1
    assert r['linkedin']['created'] >= 1
    assert r['gmail_interactions'] == 3
    assert r['whatsapp_interactions'] >= 2
    assert r['life_events'] >= 2
    assert r['reminders'] >= 2
    assert len(r['meeting_briefs']) == 2
    assert r['meeting_briefs'][0]['brief']['attendees'][0].get('person',{}).get('name') == 'Maya Singh'
    assert r['queries']['company']['results'][0]['name'] == 'Maya Singh'
    assert len(r['queries']['stale']['results']) >= 1
    assert len(r['queries']['promises']['results']) >= 1

def test_identity_resolution_and_person_brief():
    c=con(); seed_and_run(c)
    p=resolve_person(c,email='MAYA@ECODATA.EXAMPLE')
    assert p and p['name']=='Maya Singh'
    b=person_brief(c,p['id'])
    assert b['recent_interactions']
    assert b['open_loops']

def test_provenance_is_retained():
    c=con(); seed_and_run(c)
    n=c.execute('SELECT COUNT(*) n FROM interactions WHERE source_entity_id IS NOT NULL').fetchone()['n']
    sources=c.execute('SELECT COUNT(*) n FROM source_entities').fetchone()['n']
    assert n >= 5 and sources >= 5
