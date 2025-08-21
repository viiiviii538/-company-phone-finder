import argparse
import json
import os
import pandas as pd
from .search import SearchClient
from .extract import fetch_html, parse_tel_candidates, near_address_context
from .scoring import name_similarity, addr_similarity, score
from .normalizer import normalize_addr
from .utils import detect_encoding


QUERY_TEMPLATE = "{name} {address} 電話 OR TEL site:co.jp OR site:or.jp OR site:gr.jp"


def lookup(name: str, address: str, client: SearchClient) -> list:
    query = QUERY_TEMPLATE.format(name=name, address=address)
    results = client.search(query)
    norm_addr = normalize_addr(address)
    candidates = []
    for res in results:
        try:
            html = fetch_html(res.url)
        except Exception:
            continue
        phones = parse_tel_candidates(html)
        if not phones:
            continue
        proximity = near_address_context(html, norm_addr)
        for phone, raw in phones:
            cand = {
                "phone": phone,
                "name_sim": name_similarity(name, res.title),
                "addr_sim": addr_similarity(address, html),
                "proximity": proximity,
                "url": res.url,
                "source": res.title,
            }
            cand["score"] = score(cand)
            candidates.append(cand)
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:3]


def main():
    parser = argparse.ArgumentParser(description="Lookup phone numbers from company list")
    parser.add_argument("input", help="input CSV path")
    parser.add_argument("output", help="output CSV path")
    args = parser.parse_args()

    encoding = detect_encoding(args.input)
    df = pd.read_csv(args.input, encoding=encoding)
    client = SearchClient(os.getenv("SEARCH_PROVIDER", "serpapi"))

    phone_best, phone_candidates, best_score, best_source_url = [], [], [], []
    for _, row in df.iterrows():
        candidates = lookup(row["name"], row["address"], client)
        if candidates:
            phone_best.append(candidates[0]["phone"])
            phone_candidates.append(json.dumps(candidates, ensure_ascii=False))
            best_score.append(candidates[0]["score"])
            best_source_url.append(candidates[0]["url"])
        else:
            phone_best.append("")
            phone_candidates.append("[]")
            best_score.append(0)
            best_source_url.append("")
    df["phone_best"] = phone_best
    df["phone_candidates"] = phone_candidates
    df["best_score"] = best_score
    df["best_source_url"] = best_source_url
    df.to_csv(args.output, index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
