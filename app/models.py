from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Locality(Base):
    __tablename__ = "localities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    avg_price_per_sqft = Column(Float)
    avg_monthly_rent = Column(Float)
    standard_property_size_sqft = Column(Integer)

    latitude = Column(Float)
    longitude = Column(Float)


