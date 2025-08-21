from urllib.parse import urlparse
from rapidfuzz import fuzz
from .normalizer import normalize_name, normalize_addr


def name_similarity(a: str, b: str) -> float:
    return fuzz.ratio(normalize_name(a), normalize_name(b))


def addr_similarity(a: str, b: str) -> float:
    return fuzz.ratio(normalize_addr(a), normalize_addr(b))


def domain_penalty(url: str) -> float:
    host = urlparse(url).hostname or ""
    if host.endswith(".lg.jp") or host.endswith(".go.jp"):
        return -50.0
    return 0.0


def directory_penalty(url: str) -> float:
    host = urlparse(url).hostname or ""
    directory_hosts = ["itp.ne.jp", "townpage", "japanphonebook", "tel"]
    if any(h in host for h in directory_hosts):
        return -30.0
    return 0.0


def score(candidate: dict) -> float:
    base = candidate.get("base", 0.0)
    name_sim = candidate.get("name_sim", 0.0)
    addr_sim = candidate.get("addr_sim", 0.0)
    proximity = 10.0 if candidate.get("proximity") else 0.0
    penalties = domain_penalty(candidate.get("url", "")) + directory_penalty(candidate.get("url", ""))
    return base + name_sim + addr_sim + proximity + penalties
