from __future__ import annotations

def graph(con):
    people=[dict(x) for x in con.execute('SELECT id,name,company,context,importance FROM people').fetchall()]
    edges=[]
    by_company={}
    for p in people:
        if p['company']:by_company.setdefault(p['company'].lower(),[]).append(p)
    for _,ps in by_company.items():
        for i,a in enumerate(ps):
            for b in ps[i+1:]:edges.append({'source':a['id'],'target':b['id'],'type':'same_company'})
    return {'nodes':people,'edges':edges}

def introductions(con,person_id:int):
    p=con.execute('SELECT * FROM people WHERE id=?',(person_id,)).fetchone()
    if not p:return []
    rows=con.execute('SELECT * FROM people WHERE id<>? AND (context=? OR company=?) ORDER BY importance DESC LIMIT 20',(person_id,p['context'],p['company'])).fetchall()
    return [dict(r) for r in rows]
