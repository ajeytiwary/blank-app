from __future__ import annotations
import os

def _creds():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    scopes=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']
    token=os.getenv('GOOGLE_TOKEN_FILE','config/google-token.json'); client=os.getenv('GOOGLE_CLIENT_FILE','config/google-client.json')
    creds=Credentials.from_authorized_user_file(token,scopes) if os.path.exists(token) else None
    if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
    if not creds or not creds.valid:
        flow=InstalledAppFlow.from_client_secrets_file(client,scopes); creds=flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token),exist_ok=True); open(token,'w').write(creds.to_json())
    return creds

def gmail_messages(limit=100):
    from googleapiclient.discovery import build
    svc=build('gmail','v1',credentials=_creds()); ids=svc.users().messages().list(userId='me',maxResults=limit).execute().get('messages',[]); out=[]
    for item in ids:
        m=svc.users().messages().get(userId='me',id=item['id'],format='metadata',metadataHeaders=['From','To','Subject','Date']).execute(); h={x['name'].lower():x['value'] for x in m.get('payload',{}).get('headers',[])}
        out.append({'id':m['id'],'thread_id':m.get('threadId'),'from':h.get('from',''),'to':h.get('to',''),'subject':h.get('subject',''),'date':h.get('date',''),'snippet':m.get('snippet','')})
    return out

def calendar_events(limit=50):
    from googleapiclient.discovery import build
    from datetime import datetime,timezone
    svc=build('calendar','v3',credentials=_creds()); now=datetime.now(timezone.utc).isoformat(); events=svc.events().list(calendarId='primary',timeMin=now,maxResults=limit,singleEvents=True,orderBy='startTime').execute().get('items',[])
    return [{'id':e['id'],'summary':e.get('summary',''),'start':e.get('start',{}).get('dateTime',e.get('start',{}).get('date')),'attendees':e.get('attendees',[]),'description':e.get('description','')} for e in events]
