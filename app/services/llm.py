from __future__ import annotations
import json, os, urllib.request

SYSTEM = '''You extract relationship CRM information. Return strict JSON only with keys summary, person_name, company, facts, life_events, commitments, follow_up. facts is an array of {category,value,confidence,sensitive}; life_events an array of {type,value,date,confidence}; commitments an array of {text,due_at,confidence}. Never invent facts. Use null when unknown.'''

def extract(text: str) -> dict:
    base=os.getenv('RELATIONSHIPOS_LLM_URL','').rstrip('/')
    model=os.getenv('RELATIONSHIPOS_LLM_MODEL','')
    key=os.getenv('RELATIONSHIPOS_LLM_API_KEY','')
    if not base or not model:
        return {'summary':text[:500],'person_name':None,'company':None,'facts':[],'life_events':[],'commitments':[],'follow_up':None,'provider':'fallback'}
    payload=json.dumps({'model':model,'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':text}]}).encode()
    req=urllib.request.Request(base+'/chat/completions',data=payload,headers={'Content-Type':'application/json',**({'Authorization':'Bearer '+key} if key else {})})
    with urllib.request.urlopen(req,timeout=60) as r:
        raw=json.load(r)
    result=json.loads(raw['choices'][0]['message']['content'])
    result['provider']='llm'
    return result
