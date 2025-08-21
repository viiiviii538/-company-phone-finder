from src.extract import normalize_phone


def test_normalize_phone_fullwidth():
    assert normalize_phone("０３−１２３４−５６７８") == "03-1234-5678"


def test_normalize_phone_international():
    assert normalize_phone("+81-3-1234-5678") == "+81-3-1234-5678"
