from app.services.relationship import score

def test_stale_high_importance_is_prioritized():
    r=score(10,None,2,0)
    assert r['priority'] >= 80
    assert r['going_cold'] is True

def test_recent_contact_is_healthy():
    from datetime import datetime, timezone
    r=score(7,datetime.now(timezone.utc).isoformat())
    assert r['health'] >= 9
    assert r['going_cold'] is False
