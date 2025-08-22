from .search import SearchClient
from .extract import fetch_html, parse_tel_candidates
from .normalizer import normalize_name, normalize_addr
from .scoring import similarity, calc_score


def lookup(name: str, address: str):
    name_n = normalize_name(name)
    addr_n = normalize_addr(address)
    query = _build_query(name, address)
    results = _search_results(query)
    candidates = []
    for result in results:
        candidates.extend(_candidates_from_result(result, name_n, addr_n))
    return _select_best(candidates)


def _build_query(name: str, address: str) -> str:
    return f"{name} {address} 電話 OR TEL"


def _search_results(query: str):
    client = SearchClient()
    return client.search(query)


def _candidates_from_result(result, name_n: str, addr_n: str):
    try:
        html_text = fetch_html(result.url)
    except Exception:
        return []
    near_addr = _mention_addr(html_text, addr_n)
    tels = parse_tel_candidates(html_text)
    return [
        _make_candidate(tel, html_text, result, name_n, addr_n, near_addr)
        for tel, _ in tels
    ]


def _make_candidate(tel: str, html_text: str, result, name_n: str, addr_n: str, near_addr: bool):
    score = calc_score(name_n, addr_n, near_addr, result.url)
    score += similarity(name_n, _strip_title(result)) * 0.2
    score += similarity(addr_n, _shorten_addr(html_text)) * 0.2
    return {
        "phone": _normalize_domestic(tel),
        "score": round(min(score, 100), 1),
        "url": result.url,
        "source": "page",
    }


def _select_best(cands):
    best = {}
    for c in sorted(cands, key=lambda x: -x["score"]):
        best.setdefault(c["phone"], c)
    return list(best.values())[:3]


def _mention_addr(htm: str, addr_n: str) -> bool:
    # 住所断片（市区町村名など）を拾って近接とみなすゆる判定
    import re
    k = addr_n[:10]
    return bool(re.search(re.escape(k), htm))


def _strip_title(r) -> str:
    return r.title.replace("|", " ").split("-")[0]


def _shorten_addr(htm: str) -> str:
    # 住所行っぽい1行を返して比較に使う（簡易）
    for key in ("住所", "所在地", "本社"):
        i = htm.find(key)
        if i >= 0:
            return htm[i : i + 40]
    return ""


def _normalize_domestic(tel: str) -> str:
    # +81 → 0 始まりに変換（簡易）
    if tel.startswith("+81-"):
        return "0" + tel[4:]
    return tel

