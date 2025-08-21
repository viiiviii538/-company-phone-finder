import os, pandas as pd, chardet
from dotenv import load_dotenv
from src.service import lookup

load_dotenv()

def read_csv_auto(path:str)->pd.DataFrame:
    raw = open(path, 'rb').read(40000)
    enc = chardet.detect(raw).get('encoding') or 'utf-8'
    return pd.read_csv(path, encoding=enc)

def run(in_path:str, out_path:str):
    df = read_csv_auto(in_path)
    assert {'法人名','住所'} <= set(df.columns), "列名は『法人名』『住所』が必要です"
    bests, candjson, scores, urls = [], [], [], []
    for _, row in df.iterrows():
        c = lookup(row['法人名'], row['住所'])
        bests.append(c[0]['phone'] if c else "")
        candjson.append(c)
        scores.append(c[0]['score'] if c else 0)
        urls.append(c[0]['url'] if c else "")
    df['phone_best']=bests
    df['phone_candidates']=df.apply(lambda x: "", axis=1)
    df['phone_candidates']=df['phone_candidates'].mask(True, [c for c in candjson]) # ダミー初期化回避
    df['best_score']=scores
    df['best_source_url']=urls
    df.to_csv(out_path, index=False, encoding='utf-8-sig')

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--in", dest="inf", required=True)
    p.add_argument("--out", dest="outf", default="out.csv")
    args=p.parse_args()
    run(args.inf, args.outf)
