from typing import List
from pydantic import BaseModel


class Candidate(BaseModel):
    phone: str
    score: float
    url: str
    source: str


class LookupRequest(BaseModel):
    name: str
    address: str


class LookupResponse(BaseModel):
    candidates: List[Candidate]
