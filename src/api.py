from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import os
import io
import json
import pandas as pd
from .models import LookupRequest, LookupResponse, Candidate
from .main import lookup
from .search import SearchClient
from .utils import detect_encoding_bytes

app = FastAPI(title="Company Phone Finder")
client = SearchClient(os.getenv("SEARCH_PROVIDER", "serpapi"))


@app.post("/lookup", response_model=LookupResponse)
def api_lookup(req: LookupRequest):
    cands = lookup(req.name, req.address, client)
    return {"candidates": cands}


@app.post("/batch")
async def api_batch(file: UploadFile = File(...)):
    content = await file.read()
    encoding = detect_encoding_bytes(content)
    df = pd.read_csv(io.BytesIO(content), encoding=encoding)
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
    csv_bytes = df.to_csv(index=False, encoding="utf-8").encode("utf-8")
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=output.csv"})
