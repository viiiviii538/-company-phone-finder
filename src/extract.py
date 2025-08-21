import re, requests
from lxml import html

TEL_RE = re.compile(r'(?:\+81\-?\d{1,2}|\(?0\d{1,4}\)?)\-?\d{1,4}\-?\d{4}')

def fetch_html(url:str)->str:
    r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    return r.text

def parse_tel_candidates(htm:str):
    tree = html.fromstring(htm)
    texts = tree.xpath('//text()')
    out=[]
    for t in texts:
        for m in TEL_RE.findall(t):
            tel = normalize_phone(m)
            if tel:
                out.append((tel, t.strip()[:80]))
    return list(dict.fromkeys(out))  # dedupe

def normalize_phone(s:str)->str:
    s = s.replace('（','(').replace('）',')').replace('ー','-').replace('－','-')
    s = re.sub(r'[^\d\-\+\(\)]','', s)
    s = s.replace('(+81)','+81')
    # 全角→半角は割愛（必要なら normalizer._zen2han を流用）
    # 国内表記を標準化
    s = s.replace('+81-0', '+81-')
    return s
