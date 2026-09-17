from __future__ import annotations
import email.utils, re
from datetime import datetime, timezone
from .mock import payload
from .identity import resolve_person
from .importers import import_linkedin_csv, parse_whatsapp
from .life_events import detect
from .briefing import meeting_brief
from .query import crm_query

SCHEMA='''
CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,company TEXT DEFAULT '',role TEXT DEFAULT '',email TEXT DEFAULT '',phone TEXT DEFAULT '',context TEXT DEFAULT 'personal',notes TEXT DEFAULT '',importance INTEGER DEFAULT 5,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_entities(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT NOT NULL,external_id TEXT,raw_text TEXT NOT NULL,received_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS interactions(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,channel TEXT DEFAULT 'note',summary TEXT NOT NULL,happened_at TEXT NOT NULL,source_entity_id INTEGER);
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER,text TEXT NOT NULL,due_at TEXT,done INTEGER DEFAULT 0,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,category TEXT DEFAULT 'general',value TEXT NOT NULL,sensitive INTEGER DEFAULT 0,confirmed INTEGER DEFAULT 0,source_entity_id INTEGER,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS candidate_facts(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,category TEXT,value TEXT NOT NULL,confidence REAL DEFAULT 0,sensitive INTEGER DEFAULT 0,source_entity_id INTEGER,status TEXT DEFAULT 'pending',created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS life_events(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,event_type TEXT NOT NULL,event_date TEXT,evidence TEXT,source_entity_id INTEGER,created_at TEXT NOT NULL);
'''
def now(): return datetime.now(timezone.utc).isoformat()
def addr(v):
    name,email=email.utils.parseaddr(v or '')
    return name.strip(),email.strip().lower()
def ensure_person(con, name, email='', company='', role='', context='personal', importance=5):
    p=resolve_person(con,email=email,name=name,company=company)
    if p:return p
    ts=now(); cur=con.execute('INSERT INTO people(name,company,role,email,context,importance,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)',(name or email,company,role,email,context,importance,ts,ts)); con.commit(); return con.execute('SELECT * FROM people WHERE id=?',(cur.lastrowid,)).fetchone()
def add_source(con, source, external_id, raw):
    cur=con.execute('INSERT INTO source_entities(source,external_id,raw_text,received_at) VALUES(?,?,?,?)',(source,external_id,raw,now())); return cur.lastrowid
def extract_commitment(text):
    m=re.search(r'(?i)(?:please |can you |i will |i’ll )(.{4,100}?)(?:\.|$)',text)
    return m.group(1).strip() if m else None
def seed_and_run(con):
    con.executescript(SCHEMA)
    for p in payload()['people']: ensure_person(con,**p)
    li=import_linkedin_csv(con,payload()['linkedin_csv'])
    gmail_count=events=reminders=0
    for m in payload()['gmail']:
        fn,fe=addr(m['from']); tn,te=addr(m['to']); external=(fn,fe) if fe!='me@example.com' else (tn,te)
        p=ensure_person(con,external[0] or external[1],external[1]); sid=add_source(con,'gmail',m['id'],m['body']); con.execute('INSERT INTO interactions(person_id,channel,summary,happened_at,source_entity_id) VALUES(?,?,?,?,?)',(p['id'],'email',m['subject']+': '+m['body'],m['date'],sid)); gmail_count+=1
        for ev in detect(m['body']):
            con.execute('INSERT INTO life_events(person_id,event_type,event_date,evidence,source_entity_id,created_at) VALUES(?,?,?,?,?,?)',(p['id'],ev['type'],(ev.get('dates') or [None])[0],ev['evidence'],sid,now())); events+=1
        c=extract_commitment(m['body'])
        if c: con.execute('INSERT INTO reminders(person_id,text,created_at) VALUES(?,?,?)',(p['id'],c,now())); reminders+=1
    wa=parse_whatsapp(payload()['whatsapp']); whatsapp_count=0
    for i,x in enumerate(wa):
        if x['sender'].lower()=='ajay': continue
        p=ensure_person(con,x['sender']); sid=add_source(con,'whatsapp',f'w{i}',x['text']); con.execute('INSERT INTO interactions(person_id,channel,summary,happened_at,source_entity_id) VALUES(?,?,?,?,?)',(p['id'],'whatsapp',x['text'],now(),sid)); whatsapp_count+=1
        for ev in detect(x['text']): con.execute('INSERT INTO life_events(person_id,event_type,event_date,evidence,source_entity_id,created_at) VALUES(?,?,?,?,?,?)',(p['id'],ev['type'],(ev.get('dates') or [None])[0],ev['evidence'],sid,now())); events+=1
    con.commit()
    briefs=[]
    for ev in payload()['calendar']:
        briefs.append({'event':ev,'brief':meeting_brief(con,[{'email':a['email'],'name':a.get('displayName','')} for a in ev['attendees']])})
    stale=crm_query(con,"Who haven't I contacted recently?"); promises=crm_query(con,'What did I promise?'); known=crm_query(con,'Who do I know at EcoData?')
    return {'ok':True,'seeded_people':con.execute('SELECT COUNT(*) n FROM people').fetchone()['n'],'linkedin':li,'gmail_interactions':gmail_count,'whatsapp_interactions':whatsapp_count,'life_events':events,'reminders':reminders,'meeting_briefs':briefs,'queries':{'stale':stale,'promises':promises,'company':known}}
