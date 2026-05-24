from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.address_schema import (
    AddressCreate, 
    AddressUpdate, 
    AddressResponse, 
    AddressNearbyResponse
)
from app.services.address_service import AddressService
from typing import List

router = APIRouter()

@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED, summary="Create a new address")
def create_address(address_in: AddressCreate, db: Session = Depends(get_db)) -> AddressResponse:
    """
    Creates a new address in the database book.
    Validates coordinates and empty strings at the API boundary.
    """
    return AddressService.create_address(db, address_in)

@router.get("/", response_model=List[AddressResponse], summary="Retrieve all addresses paginated")
def get_all_addresses(
    page: int = Query(1, ge=1, description="Page number of records"),
    limit: int = Query(10, ge=1, le=100, description="Maximum items per page"),
    db: Session = Depends(get_db)
) -> List[AddressResponse]:
    """
    Fetches all addresses from the database with pagination query offsets.
    """
    return AddressService.get_all_addresses(db, page, limit)

@router.get("/nearby", response_model=List[AddressNearbyResponse], summary="Find addresses within geodesic radius")
def get_nearby_addresses(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Target search latitude coordinate"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Target search longitude coordinate"),
    distance_km: float = Query(..., ge=0.0, description="Maximum search distance in kilometers"),
    db: Session = Depends(get_db)
) -> List[AddressNearbyResponse]:
    """
    Retrieves all addresses within a specified distance in kilometers from target coordinates.
    Resulting list is ordered by geographic proximity (nearest first).
    """
    raw_results = AddressService.get_nearby_addresses(db, latitude, longitude, distance_km)
    
    # Construct structured output containing calculated distance
    response_data = []
    for addr, dist in raw_results:
        response_data.append({
            "id": addr.id,
            "name": addr.name,
            "street": addr.street,
            "city": addr.city,
            "state": addr.state,
            "country": addr.country,
            "latitude": addr.latitude,
            "longitude": addr.longitude,
            "created_at": addr.created_at,
            "updated_at": addr.updated_at,
            "distance_km": round(dist, 4)  # High resolution rounded to 4 decimals
        })
    return response_data

@router.get("/{id}", response_model=AddressResponse, summary="Retrieve a single address by ID")
def get_address_by_id(id: int, db: Session = Depends(get_db)) -> AddressResponse:
    """
    Fetches a single address record by its primary key ID. Raises 404 if missing.
    """
    return AddressService.get_address_by_id(db, id)

@router.put("/{id}", response_model=AddressResponse, summary="Update address fields by ID")
def update_address(
    id: int, 
    address_in: AddressUpdate, 
    db: Session = Depends(get_db)
) -> AddressResponse:
    """
    Updates specified fields of an existing address using patch semantics.
    """
    return AddressService.update_address(db, id, address_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an address record by ID")
def delete_address(id: int, db: Session = Depends(get_db)) -> None:
    """
    Removes an address from the address book using its database primary ID.
    """
    AddressService.delete_address(db, id)
    return None
