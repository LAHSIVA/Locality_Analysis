from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Locality

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# CORS: tells browser allows external requests

@app.get("/locality/{name}")
def get_locality_yield(name: str, db: Session = Depends(get_db)):
    locality = db.query(Locality).filter(Locality.name.ilike(name)).first()

    if not locality:
        raise HTTPException(status_code=404, detail="Locality not found")

    annual_rent = locality.avg_monthly_rent * 12
    property_value = locality.avg_price_per_sqft * locality.standard_property_size_sqft
    rental_yield = (annual_rent / property_value) * 100

    return {
        "locality": locality.name,
        "avg_price_per_sqft": locality.avg_price_per_sqft,
        "avg_monthly_rent": locality.avg_monthly_rent,
        "rental_yield_percent": round(rental_yield, 2)
    }

# Depends(get_db) --> Injects DB Session safely 

@app.get("/locality/{name}/finance")
def locality_financials(name: str, db: Session = Depends(get_db)):
    locality = db.query(Locality).filter(Locality.name.ilike(name)).first()

    if not locality:
        raise HTTPException(status_code=404, detail="Locality not found")

    # --- Base values ---
    annual_rent = locality.avg_monthly_rent * 12
    maintenance_cost = annual_rent * 0.10
    net_annual_rent = annual_rent - maintenance_cost

    property_value = locality.avg_price_per_sqft * locality.standard_property_size_sqft

    # --- Payback Period ---
    payback_years = property_value / net_annual_rent

    # --- Appreciation (10 years @ 5%) ---
    appreciation_rate = 0.05
    appreciated_value = property_value * ((1 + appreciation_rate) ** 10)
    appreciation_gain = appreciated_value - property_value

    # --- Total ROI ---
    total_rental_income = net_annual_rent * 10
    total_gain = total_rental_income + appreciation_gain
    roi_percent = (total_gain / property_value) * 100

    return {
        "locality": locality.name,
        "latitude": locality.latitude,
        "longitude": locality.longitude,
        "property_value": round(property_value, 2),
        "annual_net_rent": round(net_annual_rent, 2),
        "payback_period_years": round(payback_years, 1),
        "ten_year_roi_percent": round(roi_percent, 2)
    }

@app.get("/localities/finance")
def all_localities_finance(
    max_payback: Optional[float] = Query(None, description="Maximum payback period in years"),
    min_roi: Optional[float] = Query(None, description="Minimum 10-year ROI percent"),
    db: Session = Depends(get_db)
):
    # -----------------------------------
    # 1️⃣ START WITH BASE QUERY
    # -----------------------------------
    query = db.query(Locality)

    # -----------------------------------
    # 2️⃣ APPROXIMATE DB-LEVEL FILTERING
    # -----------------------------------
    if max_payback is not None:
        # annual_rent / property_value >= 1 / max_payback
        query = query.filter(
            (Locality.avg_monthly_rent * 12) /
            (Locality.avg_price_per_sqft * Locality.standard_property_size_sqft)
            >= (1 / max_payback)
        )

    # Pull only pre-filtered rows
    localities = query.all()

    # -----------------------------------
    # 3️⃣ EXACT FINANCE LOGIC (PYTHON)
    # -----------------------------------
    results = []

    for loc in localities:
        # --- Finance calculations ---
        annual_rent = loc.avg_monthly_rent * 12
        maintenance_cost = annual_rent * 0.10
        net_annual_rent = annual_rent - maintenance_cost

        property_value = loc.avg_price_per_sqft * loc.standard_property_size_sqft

        payback_years = property_value / net_annual_rent

        appreciation_rate = 0.05
        appreciated_value = property_value * ((1 + appreciation_rate) ** 10)
        appreciation_gain = appreciated_value - property_value

        total_rental_income = net_annual_rent * 10
        total_gain = total_rental_income + appreciation_gain
        roi_percent = (total_gain / property_value) * 100

        # --- Exact backend filtering ---
        if max_payback is not None and payback_years > max_payback:
            continue

        if min_roi is not None and roi_percent < min_roi:
            continue

        results.append({
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "payback_period_years": round(payback_years, 1),
            "ten_year_roi_percent": round(roi_percent, 2)
        })

    return results