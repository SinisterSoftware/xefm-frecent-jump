from frecent_jump.logic import score

def test_score_weights_recent_visits_more_heavily():
    now = 100000
    assert score(2, now - 10, now) > score(2, now - 8 * 86400, now)
