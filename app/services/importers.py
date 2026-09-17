from __future__ import annotations
import csv, io, re
from datetime import datetime, timezone
from .identity import resolve_person

def import_linkedin_csv(con, text:str):
    rows=list(csv.DictReader(io.StringIO(text))); created=matched=0
    for r in rows:
        name=' '.join(filter(None,[r.get('First Name',''),r.get('Last Name','')])).strip() or r.get('Name','')
        email=r.get('Email Address','') or r.get('Email',''); company=r.get('Company','') or r.get('Company Name','')
        p=resolve_person(con,email=email,name=name,company=company)
        if p: matched+=1; continue
        ts=datetime.now(timezone.utc).isoformat(); con.execute('INSERT INTO people(name,company,email,context,created_at,updated_at) VALUES(?,?,?,?,?,?)',(name or email,company,email,'business',ts,ts)); created+=1
    con.commit(); return {'created':created,'matched':matched,'rows':len(rows)}

def parse_whatsapp(text:str):
    pattern=re.compile(r'^(?:\[)?(\d{1,2}[/.]\d{1,2}[/.]\d{2,4}),?\s+(\d{1,2}:\d{2})(?:\])?\s*-?\s*([^:]+):\s*(.*)$')
    out=[]
    for line in text.splitlines():
        m=pattern.match(line)
        if m: out.append({'date':m.group(1),'time':m.group(2),'sender':m.group(3).strip(),'text':m.group(4)})
        elif out: out[-1]['text']+='\n'+line
    return out
