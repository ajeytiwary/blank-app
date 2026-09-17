from app.services.life_events import detect
from app.services.identity import norm_email,norm_phone
from app.services.relationship import relationship_score

def test_identity_normalization():
    assert norm_email(' A@B.COM ')=='a@b.com'
    assert norm_phone('+31 (0)6 1234 5678').endswith('0612345678')

def test_life_event_detection():
    assert any(x['type']=='job' for x in detect('She started a new job at Acme'))
    assert any(x['type']=='birthday' for x in detect('His birthday is Sep 22'))

def test_relationship_score_bounds():
    assert 0 <= relationship_score(importance=5, days_since_contact=30, desired_cadence_days=30, open_loops=0) <= 10
