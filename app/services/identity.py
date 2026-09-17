from __future__ import annotations
import re
from difflib import SequenceMatcher

def norm_email(v:str)->str: return (v or '').strip().lower()
def norm_phone(v:str)->str: return re.sub(r'\D','',v or '')[-12:]
def norm_name(v:str)->str: return re.sub(r'\s+',' ',(v or '').strip().lower())

def resolve_person(con, *, email='', phone='', name='', company=''):
    e,p,n=norm_email(email),norm_phone(phone),norm_name(name)
    if e:
        r=con.execute('SELECT * FROM people WHERE lower(email)=? LIMIT 1',(e,)).fetchone()
        if r:return r
    if p:
        for r in con.execute("SELECT * FROM people WHERE phone<>''").fetchall():
            if norm_phone(r['phone'])==p:return r
    if n:
        rows=con.execute('SELECT * FROM people').fetchall(); best=None; score=0
        for r in rows:
            s=SequenceMatcher(None,n,norm_name(r['name'])).ratio()
            if company and r['company'] and company.lower()==r['company'].lower(): s+=.08
            if s>score:best,score=r,s
        if best is not None and score>=.88:return best
    return None
