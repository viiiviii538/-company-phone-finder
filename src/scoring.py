from rapidfuzz import fuzz
from urllib.parse import urlparse

BAD_DOMAINS = ('.lg.jp','.go.jp')
DIR_HINTS = ('itp.ne.jp','townpage','denwaban','telbook','050plus','jpnumber')

def domain_penalty(url:str)->int:
    host = urlparse(url).hostname or ''
    p = 0
    if any(host.endswith(d) for d in BAD_DOMAINS):
        p += 40
    if any(h in host for h in DIR_HINTS):
        p += 25
    return p

def similarity(a:str,b:str)->int:
    return int(fuzz.token_set_ratio(a,b))

def calc_score(name_norm, addr_norm, page_text_near_addr:bool, url:str)->float:
    base = 40
    if page_text_near_addr: base += 20
    pen = domain_penalty(url)
    score = max(0, base - pen)
    # name/addrは外側で渡して加点してください（例）
    return score
