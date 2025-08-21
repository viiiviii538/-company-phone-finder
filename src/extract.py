import re
import unicodedata
from typing import List, Tuple
import requests
from lxml import html

TEL_PATTERN = re.compile(r"(?:\+81[-\s]?|0)(?:[1-9]\d{0,3})[-\s]?\d{1,4}[-\s]?\d{3,4}")


def fetch_html(url: str) -> str:
    """Fetch HTML text from a URL with timeout."""
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return r.text


def normalize_phone(raw: str) -> str:
    """Normalize Japanese phone numbers to standard hyphenated form."""
    s = unicodedata.normalize("NFKC", raw)
    digits = re.sub(r"[^0-9]", "", s)
    if digits.startswith("81") and not digits.startswith("810"):
        digits = "+" + digits
    elif digits.startswith("810"):
        digits = "+81" + digits[3:]
    if digits.startswith("+81"):
        num = digits[3:]
        if num.startswith("0"):
            num = num[1:]
        if len(num) == 9:
            return f"+81-{num[:1]}-{num[1:5]}-{num[5:]}"
        if len(num) == 10:
            return f"+81-{num[:2]}-{num[2:6]}-{num[6:]}"
        return "+81-" + num
    else:
        if len(digits) == 10:
            if digits.startswith("0") and digits[1] in "123456789":
                return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        if len(digits) == 11:
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return digits


def parse_tel_candidates(html_text: str) -> List[Tuple[str, str]]:
    doc = html.fromstring(html_text)
    text = doc.text_content()
    candidates = []
    for m in TEL_PATTERN.finditer(text):
        normalized = normalize_phone(m.group())
        candidates.append((normalized, m.group()))
    return candidates


def near_address_context(html_text: str, normalized_addr: str) -> bool:
    doc = html.fromstring(html_text)
    text = unicodedata.normalize("NFKC", doc.text_content())
    return normalized_addr in text
