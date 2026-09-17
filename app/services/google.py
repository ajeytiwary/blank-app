from __future__ import annotations
import os
from pathlib import Path
SCOPES=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly','openid','https://www.googleapis.com/auth/userinfo.email']

def configured():
    return bool(os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'))

def token_dir()->Path:
    p=Path(os.getenv('RELATIONSHIPOS_TOKEN_DIR','data/tokens')); p.mkdir(parents=True,exist_ok=True); return p

def status():
    return {'configured':configured(),'scopes':SCOPES,'token_dir':str(token_dir()),'mode':'read-only'}

# OAuth callback/sync implementation deliberately lives behind this adapter.
# Tokens must remain outside git. Multiple accounts use one token file per account.
