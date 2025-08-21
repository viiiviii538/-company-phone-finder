from src.scoring import name_similarity, addr_similarity


def test_name_similarity_threshold():
    assert name_similarity("株式会社テスト", "(株)テスト") > 90


def test_addr_similarity_threshold():
    assert addr_similarity("東京都千代田区1-1", "東京都 千代田区１−１") > 90
