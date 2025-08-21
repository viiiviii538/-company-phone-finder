from pydantic import BaseModel
from typing import List, Optional

class LookupIn(BaseModel):
    name: str
    address: str

class Candidate(BaseModel):
    phone: str
    score: float
    url: str
    source: str

class LookupOut(BaseModel):
    candidates: List[Candidate]
