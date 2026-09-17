from __future__ import annotations
from datetime import datetime, timezone

def score(importance:int,last_contact:str|None,open_loops:int=0,upcoming_events:int=0)->dict:
    days=999
    if last_contact:
        try: days=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(last_contact.replace('Z','+00:00'))).days)
        except Exception: pass
    cadence=max(7,70-(importance*6))
    staleness=min(1.0,days/cadence)
    priority=min(100,round(importance*5+staleness*35+min(open_loops,3)*6+min(upcoming_events,2)*4))
    health=max(0,round(10-(staleness*5)-min(open_loops,3)*.5,1))
    return {'priority':priority,'health':health,'days_since_contact':days,'target_cadence_days':cadence,'going_cold':days>cadence}
