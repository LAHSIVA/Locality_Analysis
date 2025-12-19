# Orchestration Only

from typing import Optional
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db
from app.cache import finance_cache
from app.repositories.locality_repo import get_localities
from app.services.finance_service import calculate_financials

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/localities/finance")
def all_localities_finance(
    max_payback: Optional[float] = Query(None),
    min_roi: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    cache_key = (max_payback, min_roi)
    if cache_key in finance_cache:
        return finance_cache[cache_key]

    min_rent_ratio = None
    if max_payback is not None:
        min_rent_ratio = 1 / max_payback

    localities = get_localities(db, min_rent_ratio)

    results = []
    for loc in localities:
        result = calculate_financials(loc, max_payback, min_roi)
        if result:
            results.append(result)

    finance_cache[cache_key] = results
    return results
