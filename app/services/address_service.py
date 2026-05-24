from sqlalchemy.orm import Session
from app.database.models import Address
from app.schemas.address_schema import AddressCreate, AddressUpdate
from app.exceptions.handlers import AddressNotFoundError
from app.utils.geo import calculate_geodesic_distance
from app.utils.logger import logger
from typing import List, Tuple

class AddressService:
    @staticmethod
    def create_address(db: Session, address_in: AddressCreate) -> Address:
        """Create a new address record in the database."""
        logger.info(f"Request to create address: '{address_in.name}' in {address_in.city}, {address_in.country}")
        db_address = Address(**address_in.model_dump())
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        logger.info(f"Successfully created address ID {db_address.id}")
        return db_address

    @staticmethod
    def get_address_by_id(db: Session, address_id: int) -> Address:
        """Fetch a specific address by its primary key ID, raising 404 if not found."""
        logger.info(f"Request to fetch address ID {address_id}")
        db_address = db.query(Address).filter(Address.id == address_id).first()
        if not db_address:
            raise AddressNotFoundError(address_id)
        return db_address

    @staticmethod
    def get_all_addresses(db: Session, page: int = 1, limit: int = 10) -> List[Address]:
        """Fetch a paginated list of all address records."""
        logger.info(f"Request to fetch addresses: page={page}, limit={limit}")
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        offset = (page - 1) * limit
        return db.query(Address).offset(offset).limit(limit).all()

    @staticmethod
    def update_address(db: Session, address_id: int, address_in: AddressUpdate) -> Address:
        """Update fields of an existing address record with patch behavior."""
        logger.info(f"Request to update address ID {address_id}")
        db_address = AddressService.get_address_by_id(db, address_id)
        
        # Grab only non-null values provided in the request
        update_data = address_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_address, key, value)
            
        db.commit()
        db.refresh(db_address)
        logger.info(f"Successfully updated address ID {address_id}")
        return db_address

    @staticmethod
    def delete_address(db: Session, address_id: int) -> None:
        """Delete an address record from the database."""
        logger.info(f"Request to delete address ID {address_id}")
        db_address = AddressService.get_address_by_id(db, address_id)
        db.delete(db_address)
        db.commit()
        logger.info(f"Successfully deleted address ID {address_id}")

    @staticmethod
    def get_nearby_addresses(
        db: Session, latitude: float, longitude: float, distance_km: float
    ) -> List[Tuple[Address, float]]:
        """
        Finds all database addresses within a given radius in kilometers from target coordinates.
        Calculates oblate-spheroid geodesic distance and sorts results by proximity.
        """
        logger.info(
            f"Request to search nearby addresses around ({latitude}, {longitude}) within {distance_km} km"
        )
        
        # Load all addresses from SQLite in memory to perform the geodesic filter calculation
        all_addresses = db.query(Address).all()
        results: List[Tuple[Address, float]] = []

        for addr in all_addresses:
            # Perform calculation using geopy standard library wrapper
            dist = calculate_geodesic_distance(latitude, longitude, addr.latitude, addr.longitude)
            if dist <= distance_km:
                results.append((addr, dist))

        # Sort the array by distance ascending (nearest first)
        results.sort(key=lambda item: item[1])
        logger.info(f"Nearby search complete: found {len(results)} matches within {distance_km} km")
        return results
