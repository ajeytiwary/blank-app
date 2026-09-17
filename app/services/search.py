from __future__ import annotations
import re
from collections import Counter

def toks(s): return re.findall(r'[a-z0-9]+',(s or '').lower())
def score(q,text):
    a,b=Counter(toks(q)),Counter(toks(text));
    if not a:return 0
    overlap=sum(min(a[k],b[k]) for k in a)
    return overlap/max(1,sum(a.values()))

def hybrid_search(con,q,limit=20):
    results=[]
    for p in con.execute('SELECT * FROM people').fetchall():
        ints=con.execute('SELECT summary FROM interactions WHERE person_id=? ORDER BY happened_at DESC LIMIT 20',(p['id'],)).fetchall()
        facts=con.execute('SELECT value FROM facts WHERE person_id=?',(p['id'],)).fetchall()
        text=' '.join([p['name'],p['company'],p['role'],p['notes']]+[x['summary'] for x in ints]+[x['value'] for x in facts])
        s=score(q,text)
        if s: results.append({'score':round(s,3),'person':dict(p)})
    return sorted(results,key=lambda x:x['score'],reverse=True)[:limit]
