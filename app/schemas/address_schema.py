from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class AddressBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name representing the address (e.g., Home, Office)")
    street: str = Field(..., min_length=1, description="Street address line")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State name")
    country: str = Field(..., min_length=1, description="Country name")
    latitude: float = Field(..., description="Latitude coordinate between -90 and 90")
    longitude: float = Field(..., description="Longitude coordinate between -180 and 180")

    @field_validator("name", "street", "city", "state", "country")
    @classmethod
    def prevent_empty_or_whitespace_strings(cls, v: str) -> str:
        """Reject empty strings or strings containing only whitespace characters."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Ensure latitude is mathematically valid (-90 to 90 degrees)."""
        if not -90.0 <= v <= 90.0:
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Ensure longitude is mathematically valid (-180 to 180 degrees)."""
        if not -180.0 <= v <= 180.0:
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees")
        return v

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Name representing the address (e.g., Home, Office)")
    street: Optional[str] = Field(None, min_length=1, description="Street address line")
    city: Optional[str] = Field(None, min_length=1, description="City name")
    state: Optional[str] = Field(None, min_length=1, description="State name")
    country: Optional[str] = Field(None, min_length=1, description="Country name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate between -90 and 90")
    longitude: Optional[float] = Field(None, description="Longitude coordinate between -180 and 180")

    @field_validator("name", "street", "city", "state", "country")
    @classmethod
    def prevent_empty_or_whitespace_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field cannot be empty or whitespace only")
            return v.strip()
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if not -90.0 <= v <= 90.0:
                raise ValueError("Latitude must be between -90.0 and 90.0 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if not -180.0 <= v <= 180.0:
                raise ValueError("Longitude must be between -180.0 and 180.0 degrees")
        return v

class AddressResponse(AddressBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AddressNearbyResponse(AddressResponse):
    distance_km: float

