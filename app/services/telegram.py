from __future__ import annotations
import os, urllib.request, urllib.parse, json

def configured(): return bool(os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))
def send(text:str):
    token=os.getenv('TELEGRAM_BOT_TOKEN'); chat=os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat:return {'ok':False,'reason':'not_configured'}
    data=urllib.parse.urlencode({'chat_id':chat,'text':text}).encode(); req=urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage',data=data)
    with urllib.request.urlopen(req,timeout=15) as r:return json.loads(r.read())

def daily_brief(today:dict):
    people=today.get('people_to_contact',[])[:5]; rem=today.get('reminders',[])[:5]
    lines=['RelationshipOS — today','People:']+[f"• {p['name']}" for p in people]+['Open loops:']+[f"• {r['text']}" for r in rem]
    return '\n'.join(lines)
