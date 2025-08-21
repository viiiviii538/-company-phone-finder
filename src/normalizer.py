import re

def _zen2han(s: str) -> str:
    try:
        import jaconv  # 任意
        return jaconv.z2h(s, kana=False, digit=True, ascii=True)
    except Exception:
        return s.translate(str.maketrans({'（':'(','）':')','－':'-','ー':'-','　':' '}))

def normalize_name(s: str) -> str:
    s = _zen2han(s).lower()
    s = re.sub(r'[\s\u3000]+', '', s)
    s = s.replace('株式会社','').replace('(株)','').replace('有限会社','').replace('(有)','')
    s = re.sub(r'[^\wぁ-んァ-ン一-龥\-]', '', s)
    return s

def normalize_addr(s: str) -> str:
    s = _zen2han(s)
    s = re.sub(r'\s+', '', s)
    s = s.replace('丁目','-').replace('番地','-').replace('番','-').replace('号','')
    return s
