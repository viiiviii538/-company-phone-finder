import types
import pathlib
import sys

import pytest

# Ensure repository root is on path for package imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
import src.service as service


def test_build_query():
    assert service._build_query("Foo Corp", "Tokyo") == "Foo Corp Tokyo 電話 OR TEL"


def test_normalize_domestic():
    assert service._normalize_domestic("+81-3-1234-5678") == "03-1234-5678"
    assert service._normalize_domestic("03-1234-5678") == "03-1234-5678"


def test_select_best_dedup_and_limit():
    cands = [
        {"phone": "111", "score": 90},
        {"phone": "111", "score": 80},  # lower score duplicate
        {"phone": "222", "score": 70},
        {"phone": "333", "score": 60},
        {"phone": "444", "score": 50},
    ]
    best = service._select_best(cands)
    assert best == [
        {"phone": "111", "score": 90},
        {"phone": "222", "score": 70},
        {"phone": "333", "score": 60},
    ]


def test_mention_addr_true_false():
    addr_n = "東京都新宿区西新宿1-1-1"
    html = "<div>東京都新宿区西新宿1-1-1 の会社</div>"
    assert service._mention_addr(html, addr_n) is True
    assert service._mention_addr("no address here", addr_n) is False


def test_lookup_integration(monkeypatch):
    html = "<html>住所Bar</html>"

    class DummyClient:
        def search(self, q):
            assert q == "Foo Bar 電話 OR TEL"
            return [types.SimpleNamespace(title="Foo title", url="http://example.com")]

    monkeypatch.setattr(service, "SearchClient", DummyClient)
    monkeypatch.setattr(service, "fetch_html", lambda url: html)
    monkeypatch.setattr(service, "parse_tel_candidates", lambda h: [("03-1111-2222", "ctx")])
    monkeypatch.setattr(service, "normalize_name", lambda x: x)
    monkeypatch.setattr(service, "normalize_addr", lambda x: x)
    monkeypatch.setattr(service, "calc_score", lambda *args: 50)
    monkeypatch.setattr(service, "similarity", lambda a, b: 50)

    result = service.lookup("Foo", "Bar")
    assert result == [
        {
            "phone": "03-1111-2222",
            "score": 70.0,
            "url": "http://example.com",
            "source": "page",
        }
    ]
