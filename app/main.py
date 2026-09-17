from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("RELATIONSHIPOS_DB", ROOT / "relationshipos.db"))
STATIC = ROOT / "static"

app = FastAPI(title="RelationshipOS", version="0.1.0")

SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 company TEXT DEFAULT '', role TEXT DEFAULT '', email TEXT DEFAULT '', phone TEXT DEFAULT '',
 context TEXT DEFAULT 'personal', notes TEXT DEFAULT '', importance INTEGER DEFAULT 5,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interactions (
 id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER NOT NULL,
 channel TEXT DEFAULT 'note', summary TEXT NOT NULL, happened_at TEXT NOT NULL,
 FOREIGN KEY(person_id) REFERENCES people(id)
);
CREATE TABLE IF NOT EXISTS reminders (
 id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER,
 text TEXT NOT NULL, due_at TEXT, done INTEGER DEFAULT 0, created_at TEXT NOT NULL,
 FOREIGN KEY(person_id) REFERENCES people(id)
);
CREATE TABLE IF NOT EXISTS facts (
 id INTEGER PRIMARY KEY AUTOINCREMENT, person_id INTEGER NOT NULL,
 category TEXT DEFAULT 'general', value TEXT NOT NULL, sensitive INTEGER DEFAULT 0,
 confirmed INTEGER DEFAULT 0, created_at TEXT NOT NULL,
 FOREIGN KEY(person_id) REFERENCES people(id)
);
"""

def now(): return datetime.now(timezone.utc).isoformat()
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con

def rowdict(r): return dict(r) if r else None

class PersonIn(BaseModel):
    name: str = Field(min_length=1)
    company: str = ""
    role: str = ""
    email: str = ""
    phone: str = ""
    context: str = "personal"
    notes: str = ""
    importance: int = Field(default=5, ge=1, le=10)

class InteractionIn(BaseModel):
    person_id: int
    summary: str = Field(min_length=1)
    channel: str = "note"
    happened_at: Optional[str] = None

class ReminderIn(BaseModel):
    text: str = Field(min_length=1)
    person_id: Optional[int] = None
    due_at: Optional[str] = None

class VoiceNoteIn(BaseModel):
    transcript: str = Field(min_length=1)
    person_id: Optional[int] = None

@app.get("/api/health")
def health(): return {"ok": True, "version": "0.1.0"}

@app.get("/api/people")
def people():
    con=db(); rows=con.execute("SELECT * FROM people ORDER BY name COLLATE NOCASE").fetchall(); con.close()
    return [rowdict(r) for r in rows]

@app.post("/api/people")
def create_person(p: PersonIn):
    con=db(); ts=now()
    cur=con.execute("INSERT INTO people(name,company,role,email,phone,context,notes,importance,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(p.name,p.company,p.role,p.email,p.phone,p.context,p.notes,p.importance,ts,ts)); con.commit()
    r=con.execute("SELECT * FROM people WHERE id=?",(cur.lastrowid,)).fetchone(); con.close(); return rowdict(r)

@app.get("/api/people/{person_id}")
def person(person_id:int):
    con=db(); p=con.execute("SELECT * FROM people WHERE id=?",(person_id,)).fetchone()
    if not p: con.close(); raise HTTPException(404,"Person not found")
    interactions=con.execute("SELECT * FROM interactions WHERE person_id=? ORDER BY happened_at DESC",(person_id,)).fetchall()
    reminders=con.execute("SELECT * FROM reminders WHERE person_id=? AND done=0 ORDER BY due_at",(person_id,)).fetchall()
    facts=con.execute("SELECT * FROM facts WHERE person_id=? ORDER BY created_at DESC",(person_id,)).fetchall(); con.close()
    return {**rowdict(p),"interactions":[rowdict(x) for x in interactions],"reminders":[rowdict(x) for x in reminders],"facts":[rowdict(x) for x in facts]}

@app.post("/api/interactions")
def add_interaction(i: InteractionIn):
    con=db()
    if not con.execute("SELECT 1 FROM people WHERE id=?",(i.person_id,)).fetchone(): con.close(); raise HTTPException(404,"Person not found")
    happened=i.happened_at or now(); cur=con.execute("INSERT INTO interactions(person_id,channel,summary,happened_at) VALUES(?,?,?,?)",(i.person_id,i.channel,i.summary,happened)); con.execute("UPDATE people SET updated_at=? WHERE id=?",(now(),i.person_id)); con.commit(); con.close()
    return {"id":cur.lastrowid,"ok":True}

@app.post("/api/reminders")
def add_reminder(r: ReminderIn):
    con=db(); cur=con.execute("INSERT INTO reminders(person_id,text,due_at,created_at) VALUES(?,?,?,?)",(r.person_id,r.text,r.due_at,now())); con.commit(); con.close(); return {"id":cur.lastrowid,"ok":True}

@app.post("/api/voice-note")
def voice_note(v: VoiceNoteIn):
    """MVP ingestion seam. Browser speech recognition sends transcript here.
    Next phase swaps deterministic extraction for the configured LLM adapter."""
    if v.person_id:
        add_interaction(InteractionIn(person_id=v.person_id,summary=v.transcript,channel="voice"))
    return {"ok":True,"transcript":v.transcript,"person_id":v.person_id,"extraction":{"status":"queued","note":"LLM fact/event extraction adapter is the next integration seam"}}

@app.get("/api/today")
def today():
    con=db()
    stale=con.execute("""SELECT p.*, MAX(i.happened_at) last_contact FROM people p LEFT JOIN interactions i ON p.id=i.person_id GROUP BY p.id ORDER BY (MAX(i.happened_at) IS NOT NULL), MAX(i.happened_at) ASC, p.importance DESC LIMIT 8""").fetchall()
    reminders=con.execute("SELECT r.*,p.name person_name FROM reminders r LEFT JOIN people p ON p.id=r.person_id WHERE r.done=0 ORDER BY r.due_at IS NULL,r.due_at LIMIT 8").fetchall(); con.close()
    return {"people_to_contact":[rowdict(x) for x in stale],"reminders":[rowdict(x) for x in reminders]}

app.mount("/static", StaticFiles(directory=STATIC), name="static")
@app.get("/")
def root(): return FileResponse(STATIC / "index.html")
@app.get("/manifest.webmanifest")
def manifest(): return FileResponse(STATIC / "manifest.webmanifest", media_type="application/manifest+json")
@app.get("/sw.js")
def sw(): return FileResponse(STATIC / "sw.js", media_type="application/javascript")
