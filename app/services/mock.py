from __future__ import annotations
from datetime import datetime, timedelta, timezone

NOW=datetime.now(timezone.utc)
PEOPLE=[
 {'name':'Maya Singh','email':'maya@ecodata.example','company':'EcoData','role':'Partnerships Director','context':'MeasureNature','importance':9},
 {'name':'Pieter de Vries','email':'pieter@naturefund.example','company':'NatureFund','role':'Program Manager','context':'MeasureNature','importance':8},
 {'name':'Rahul Mehta','email':'rahul@example.com','company':'','role':'','context':'personal','importance':8},
 {'name':'Sara Khan','email':'sara@saha.example','company':'Saha','role':'Co-organiser','context':'Saha','importance':7},
]
GMAIL=[
 {'id':'g1','from':'Maya Singh <maya@ecodata.example>','to':'me@example.com','subject':'ForestPulse pilot','date':(NOW-timedelta(days=5)).isoformat(),'body':'Great speaking about ForestPulse. My daughter Anika starts school on 5 October. Please send the validation pilot proposal by 25 September.'},
 {'id':'g2','from':'me@example.com','to':'Pieter de Vries <pieter@naturefund.example>','subject':'Monitoring data','date':(NOW-timedelta(days=42)).isoformat(),'body':'I will send you the habitat monitoring comparison next week.'},
 {'id':'g3','from':'Rahul Mehta <rahul@example.com>','to':'me@example.com','subject':'Dinner','date':(NOW-timedelta(days=100)).isoformat(),'body':'My birthday is 12 November. Let us catch up soon.'},
]
CALENDAR=[
 {'id':'c1','summary':'EcoData x MeasureNature','start':(NOW+timedelta(days=1)).isoformat(),'attendees':[{'email':'maya@ecodata.example','displayName':'Maya Singh'}]},
 {'id':'c2','summary':'Saha planning','start':(NOW+timedelta(days=2)).isoformat(),'attendees':[{'email':'sara@saha.example','displayName':'Sara Khan'}]},
]
LINKEDIN_CSV='First Name,Last Name,Email Address,Company,Position,Connected On\nMaya,Singh,maya@ecodata.example,EcoData,Partnerships Director,01 Sep 2026\nRobert,Jansen,robert@greenbuyer.example,GreenBuyer,Sustainability Lead,02 Sep 2026\n'
WHATSAPP='''[01/09/2026, 09:10] Rahul Mehta: Happy to catch up. My birthday is 12 November.\n[01/09/2026, 09:12] Ajay: Great, I will call you next week.\n[05/09/2026, 15:00] Sara Khan: Can you send the venue shortlist by Friday?'''

def payload(): return {'people':PEOPLE,'gmail':GMAIL,'calendar':CALENDAR,'linkedin_csv':LINKEDIN_CSV,'whatsapp':WHATSAPP}
