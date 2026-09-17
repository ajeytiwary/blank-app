from __future__ import annotations
import os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.services.ingestion import ingest
from app.services.relationship import score
from app.services.google import status as google_status

ROOT=Path(__file__).resolve().parents[1]; DB_PATH=Path(os.getenv('RELATIONSHIPOS_DB',ROOT/'relationshipos.db')); STATIC=ROOT/'static'
app=FastAPI(title='RelationshipOS',version='0.2.0')
SCHEMA='''
CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,company TEXT DEFAULT '',role TEXT DEFAULT '',email TEXT DEFAULT '',phone TEXT DEFAULT '',context TEXT DEFAULT 'personal',notes TEXT DEFAULT '',importance INTEGER DEFAULT 5,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_entities(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT NOT NULL,external_id TEXT,raw_text TEXT NOT NULL,received_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS interactions(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,channel TEXT DEFAULT 'note',summary TEXT NOT NULL,happened_at TEXT NOT NULL,source_entity_id INTEGER,FOREIGN KEY(person_id) REFERENCES people(id));
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER,text TEXT NOT NULL,due_at TEXT,done INTEGER DEFAULT 0,created_at TEXT NOT NULL,FOREIGN KEY(person_id) REFERENCES people(id));
CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,category TEXT DEFAULT 'general',value TEXT NOT NULL,sensitive INTEGER DEFAULT 0,confirmed INTEGER DEFAULT 0,source_entity_id INTEGER,created_at TEXT NOT NULL,FOREIGN KEY(person_id) REFERENCES people(id));
CREATE TABLE IF NOT EXISTS candidate_facts(id INTEGER PRIMARY KEY AUTOINCREMENT,person_id INTEGER NOT NULL,category TEXT,value TEXT NOT NULL,confidence REAL DEFAULT 0,sensitive INTEGER DEFAULT 0,source_entity_id INTEGER,status TEXT DEFAULT 'pending',created_at TEXT NOT NULL);
'''
def now(): return datetime.now(timezone.utc).isoformat()
def db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c
def d(r): return dict(r) if r else None
class PersonIn(BaseModel):
 name:str=Field(min_length=1); company:str=''; role:str=''; email:str=''; phone:str=''; context:str='personal'; notes:str=''; importance:int=Field(default=5,ge=1,le=10)
class InteractionIn(BaseModel): person_id:int; summary:str=Field(min_length=1); channel:str='note'; happened_at:Optional[str]=None
class ReminderIn(BaseModel): text:str=Field(min_length=1); person_id:Optional[int]=None; due_at:Optional[str]=None
class VoiceNoteIn(BaseModel): transcript:str=Field(min_length=1); person_id:Optional[int]=None
class IngestIn(BaseModel): text:str=Field(min_length=1); source:str='note'; person_id:Optional[int]=None
@app.get('/api/health')
def health(): return {'ok':True,'version':'0.2.0','google':google_status()}
@app.get('/api/people')
def people():
 c=db(); rows=c.execute('SELECT * FROM people ORDER BY name COLLATE NOCASE').fetchall(); c.close(); return [d(r) for r in rows]
@app.post('/api/people')
def create_person(p:PersonIn):
 c=db(); ts=now(); cur=c.execute('INSERT INTO people(name,company,role,email,phone,context,notes,importance,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(p.name,p.company,p.role,p.email,p.phone,p.context,p.notes,p.importance,ts,ts)); c.commit(); r=c.execute('SELECT * FROM people WHERE id=?',(cur.lastrowid,)).fetchone(); c.close(); return d(r)
@app.get('/api/people/{pid}')
def person(pid:int):
 c=db(); p=c.execute('SELECT * FROM people WHERE id=?',(pid,)).fetchone()
 if not p: c.close(); raise HTTPException(404,'Person not found')
 ints=c.execute('SELECT * FROM interactions WHERE person_id=? ORDER BY happened_at DESC',(pid,)).fetchall(); rem=c.execute('SELECT * FROM reminders WHERE person_id=? AND done=0 ORDER BY due_at',(pid,)).fetchall(); facts=c.execute('SELECT * FROM facts WHERE person_id=? ORDER BY created_at DESC',(pid,)).fetchall(); cand=c.execute('SELECT * FROM candidate_facts WHERE person_id=? AND status="pending" ORDER BY created_at DESC',(pid,)).fetchall(); c.close(); return {**d(p),'interactions':[d(x) for x in ints],'reminders':[d(x) for x in rem],'facts':[d(x) for x in facts],'candidate_facts':[d(x) for x in cand]}
@app.post('/api/interactions')
def add_interaction(i:InteractionIn):
 c=db(); cur=c.execute('INSERT INTO interactions(person_id,channel,summary,happened_at) VALUES(?,?,?,?)',(i.person_id,i.channel,i.summary,i.happened_at or now())); c.commit(); c.close(); return {'id':cur.lastrowid,'ok':True}
@app.post('/api/reminders')
def add_reminder(r:ReminderIn):
 c=db(); cur=c.execute('INSERT INTO reminders(person_id,text,due_at,created_at) VALUES(?,?,?,?)',(r.person_id,r.text,r.due_at,now())); c.commit(); c.close(); return {'id':cur.lastrowid,'ok':True}
@app.post('/api/ingest')
def ingestion(x:IngestIn):
 c=db(); out=ingest(c,x.text,x.source,x.person_id); c.close(); return out
@app.post('/api/voice-note')
def voice(v:VoiceNoteIn): return ingestion(IngestIn(text=v.transcript,source='voice',person_id=v.person_id))
@app.get('/api/inbox')
def inbox():
 c=db(); rows=c.execute('SELECT cf.*,p.name person_name FROM candidate_facts cf JOIN people p ON p.id=cf.person_id WHERE cf.status="pending" ORDER BY cf.created_at DESC').fetchall(); c.close(); return [d(x) for x in rows]
@app.post('/api/inbox/{fid}/confirm')
def confirm(fid:int):
 c=db(); f=c.execute('SELECT * FROM candidate_facts WHERE id=?',(fid,)).fetchone()
 if not f: c.close(); raise HTTPException(404,'Candidate fact not found')
 c.execute('INSERT INTO facts(person_id,category,value,sensitive,confirmed,source_entity_id,created_at) VALUES(?,?,?,?,1,?,?)',(f['person_id'],f['category'],f['value'],f['sensitive'],f['source_entity_id'],now())); c.execute('UPDATE candidate_facts SET status="confirmed" WHERE id=?',(fid,)); c.commit(); c.close(); return {'ok':True}
@app.get('/api/today')
def today():
 c=db(); rows=c.execute('SELECT p.*,MAX(i.happened_at) last_contact,(SELECT COUNT(*) FROM reminders r WHERE r.person_id=p.id AND r.done=0) open_loops FROM people p LEFT JOIN interactions i ON p.id=i.person_id GROUP BY p.id').fetchall(); people=[]
 for r in rows: x=d(r); x['relationship']=score(x['importance'],x['last_contact'],x['open_loops']); people.append(x)
 people.sort(key=lambda x:x['relationship']['priority'],reverse=True); rem=c.execute('SELECT r.*,p.name person_name FROM reminders r LEFT JOIN people p ON p.id=r.person_id WHERE r.done=0 ORDER BY r.due_at IS NULL,r.due_at LIMIT 10').fetchall(); c.close(); return {'people_to_contact':people[:10],'reminders':[d(x) for x in rem]}
@app.get('/api/integrations/google')
def google(): return google_status()
app.mount('/static',StaticFiles(directory=STATIC),name='static')
@app.get('/')
def root(): return FileResponse(STATIC/'index.html')
@app.get('/manifest.webmanifest')
def manifest(): return FileResponse(STATIC/'manifest.webmanifest',media_type='application/manifest+json')
@app.get('/sw.js')
def sw(): return FileResponse(STATIC/'sw.js',media_type='application/javascript')
