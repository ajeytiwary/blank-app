from __future__ import annotations
import re
EVENTS={'birthday':['birthday','turns ','born on'],'wedding':['wedding','getting married','married'],'job':['new job','joined ','promoted','promotion'],'move':['moving to','moved to','new home'],'baby':['baby','pregnant','expecting','newborn'],'graduation':['graduated','graduation']}

def detect(text:str):
    low=text.lower(); out=[]
    for kind,keys in EVENTS.items():
        if any(k in low for k in keys): out.append({'type':kind,'evidence':text[:500]})
    dates=re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2})\b',low)
    for e in out:e['dates']=dates
    return out
