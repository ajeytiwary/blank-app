from __future__ import annotations

def crm_query(con, q:str):
    ql=q.lower().strip()
    if 'haven' in ql and ('contact' in ql or 'spoken' in ql):
        rows=con.execute('''SELECT p.id,p.name,p.company,MAX(i.happened_at) last_contact FROM people p LEFT JOIN interactions i ON i.person_id=p.id GROUP BY p.id ORDER BY last_contact IS NOT NULL,last_contact ASC LIMIT 25''').fetchall()
        return {'intent':'stale_contacts','results':[dict(r) for r in rows]}
    if 'promise' in ql or 'commit' in ql:
        rows=con.execute("SELECT r.*,p.name person_name FROM reminders r LEFT JOIN people p ON p.id=r.person_id WHERE r.done=0 ORDER BY r.due_at").fetchall()
        return {'intent':'open_commitments','results':[dict(r) for r in rows]}
    if 'who do i know at' in ql:
        company=ql.split('who do i know at',1)[1].strip(' ?')
        rows=con.execute('SELECT * FROM people WHERE lower(company) LIKE ? ORDER BY importance DESC',('%'+company+'%',)).fetchall()
        return {'intent':'company_contacts','company':company,'results':[dict(r) for r in rows]}
    rows=con.execute('SELECT * FROM people WHERE lower(name) LIKE ? OR lower(company) LIKE ? LIMIT 25',('%'+ql+'%','%'+ql+'%')).fetchall()
    return {'intent':'search','results':[dict(r) for r in rows]}
