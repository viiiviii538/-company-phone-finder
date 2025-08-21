from src.scoring import score


def test_municipal_domain_penalty():
    cand_good = {"url": "https://example.co.jp", "name_sim": 50, "addr_sim": 50, "proximity": False}
    cand_bad = {"url": "https://city.example.lg.jp", "name_sim": 50, "addr_sim": 50, "proximity": False}
    assert score(cand_bad) < score(cand_good)
