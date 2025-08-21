import re
import unicodedata


def normalize_name(name: str) -> str:
    """Normalize company names by removing common tokens and punctuation."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKC", name)
    s = s.lower()
    # Remove variations of "株式会社"
    s = re.sub(r"\(株\)|（株）|株式会社|㈱", "", s)
    # Remove punctuation and whitespace
    s = re.sub(r"[\s・,、.()（）]", "", s)
    return s


def normalize_addr(addr: str) -> str:
    """Normalize Japanese addresses by unifying width and removing spaces."""
    if not addr:
        return ""
    s = unicodedata.normalize("NFKC", addr)
    s = s.replace("−", "-")
    s = re.sub(r"\s+", "", s)
    return s
