from .search import SearchClient
from .extract import fetch_html, parse_tel_candidates
from .normalizer import normalize_name, normalize_addr
from .scoring import similarity, calc_score
import json

def lookup(name:str, address:str):
    name_n = normalize_name(name)
    addr_n = normalize_addr(address)
    q = f'{name} {address} 電話 OR TEL'
    client = SearchClient()
    results = client.search(q)

    cands=[]
    for r in results:
        try:
            h = fetch_html(r.url)
        except Exception:
            continue
        near_addr = _mention_addr(h, addr_n)
        tels = parse_tel_candidates(h)
        for tel, ctx in tels:
            s = calc_score(name_n, addr_n, near_addr, r.url)
            s += similarity(name_n, _strip_title(r)) * 0.2
            s += similarity(addr_n, _shorten_addr(h)) * 0.2
            cands.append({
                "phone": _normalize_domestic(tel),
                "score": round(min(s,100),1),
                "url": r.url,
                "source": "page"
            })
    # スコア高い順で返す、重複電話は最高スコアだけ
    best={}
    for c in sorted(cands, key=lambda x:-x["score"]):
        best.setdefault(c["phone"], c)
    return list(best.values())[:3]

def _mention_addr(htm:str, addr_n:str)->bool:
    # 住所断片（市区町村名など）を拾って近接とみなすゆる判定
    import re
    k = addr_n[:10]
    return bool(re.search(re.escape(k), htm))

def _strip_title(r)->str:
    return r.title.replace('|',' ').split('-')[0]

def _shorten_addr(htm:str)->str:
    # 住所行っぽい1行を返して比較に使う（簡易）
    for key in ("住所","所在地","本社"):
        i = htm.find(key)
        if i>=0:
            return htm[i:i+40]
    return ""

def _normalize_domestic(tel:str)->str:
    # +81 → 0 始まりに変換（簡易）
    if tel.startswith("+81-"):
        return "0"+tel[4:]
    return tel
