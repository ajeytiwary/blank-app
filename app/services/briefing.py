from __future__ import annotations

def person_brief(con, person_id:int):
    p=con.execute('SELECT * FROM people WHERE id=?',(person_id,)).fetchone()
    if not p:return None
    interactions=con.execute('SELECT channel,summary,happened_at FROM interactions WHERE person_id=? ORDER BY happened_at DESC LIMIT 8',(person_id,)).fetchall()
    facts=con.execute('SELECT category,value,confirmed FROM facts WHERE person_id=? ORDER BY confirmed DESC,created_at DESC LIMIT 12',(person_id,)).fetchall()
    reminders=con.execute('SELECT text,due_at FROM reminders WHERE person_id=? AND done=0 ORDER BY due_at LIMIT 8',(person_id,)).fetchall()
    return {'person':dict(p),'recent_interactions':[dict(x) for x in interactions],'facts':[dict(x) for x in facts],'open_loops':[dict(x) for x in reminders]}

def meeting_brief(con, attendees:list[dict]):
    from .identity import resolve_person
    out=[]
    for a in attendees:
        p=resolve_person(con,email=a.get('email',''),name=a.get('name',''))
        out.append(person_brief(con,p['id']) if p else {'unresolved':a})
    return {'attendees':out}
