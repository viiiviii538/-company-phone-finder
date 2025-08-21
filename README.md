# Company Phone Finder

CSV の法人名と住所から企業の電話番号を推定するツールです。CLI と FastAPI を備え、SerpAPI または Bing Web Search API を使用して Web から電話番号を抽出します。

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env  # API キーを設定
```

## 使い方

### CLI

```bash
python -m src.main sample/input.csv output.csv
```

入力 CSV のエンコーディングは `chardet` で自動判定します。結果 CSV には `phone_best`, `phone_candidates`, `best_score`, `best_source_url` 列が追加されます。

### API

```bash
uvicorn src.api:app --reload
```

- `POST /lookup` `{"name":"株式会社サンプル","address":"東京都千代田区1-1-1"}`
- `POST /batch` で CSV をアップロードすると、電話番号列を追加した CSV を返します。

## 注意

- 取得する HTML は 1 ページ程度に限定し、過度なスクレイピングは行わないでください。
- API 利用規約や robots.txt を遵守してください。
