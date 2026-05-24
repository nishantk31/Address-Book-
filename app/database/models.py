from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.connection import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False, index=True)
    
    # Coordinates for geodesic searches
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Audit timestamps using timezone-aware UTC dates
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Address id={self.id} name='{self.name}' city='{self.city}' lat={self.latitude} lon={self.longitude}>"
