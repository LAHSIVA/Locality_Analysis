# DB ACCESS ONLY

from sqlalchemy.orm import Session
from app.models import Locality

def get_localities(db: Session, min_rent_ratio=None):
    query = db.query(Locality)

    if min_rent_ratio is not None:
        query = query.filter(
            (Locality.avg_monthly_rent * 12) /
            (Locality.avg_price_per_sqft * Locality.standard_property_size_sqft)
            >= min_rent_ratio
        )

    return query.all()
