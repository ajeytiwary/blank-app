from __future__ import annotations
import json
from .llm import extract

def ingest(con, text:str, source:str='note', person_id:int|None=None):
    result=extract(text)
    cur=con.execute('INSERT INTO source_entities(source,external_id,raw_text,received_at) VALUES(?,?,?,datetime("now"))',(source,None,text))
    source_id=cur.lastrowid
    if person_id:
        con.execute('INSERT INTO interactions(person_id,channel,summary,happened_at,source_entity_id) VALUES(?,?,?,datetime("now"),?)',(person_id,source,result.get('summary') or text[:500],source_id))
        for f in result.get('facts',[]):
            confidence=float(f.get('confidence') or 0)
            con.execute('INSERT INTO candidate_facts(person_id,category,value,confidence,sensitive,source_entity_id,status,created_at) VALUES(?,?,?,?,?,?,?,datetime("now"))',(person_id,f.get('category','general'),f.get('value',''),confidence,1 if f.get('sensitive') else 0,source_id,'pending' if confidence<.9 or f.get('sensitive') else 'auto'))
        for c in result.get('commitments',[]):
            if c.get('text'): con.execute('INSERT INTO reminders(person_id,text,due_at,created_at) VALUES(?,?,?,datetime("now"))',(person_id,c['text'],c.get('due_at')))
    con.commit()
    return {'source_entity_id':source_id,'extraction':result}
