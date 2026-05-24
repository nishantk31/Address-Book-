from geopy.distance import geodesic
from app.utils.logger import logger

def calculate_geodesic_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the geodesic distance in kilometers between two coordinates (latitude, longitude)
    using the WGS-84 ellipsoid standard via the geopy library.
    
    :param lat1: Latitude of the first point.
    :param lon1: Longitude of the first point.
    :param lat2: Latitude of the second point.
    :param lon2: Longitude of the second point.
    :return: Distance in kilometers as a float.
    """
    try:
        coord1 = (lat1, lon1)
        coord2 = (lat2, lon2)
        
        # geopy.distance.geodesic uses the WGS-84 oblate ellipsoid by default
        distance_km = geodesic(coord1, coord2).km
        return distance_km
    except Exception as e:
        logger.error(
            f"Failed to calculate geodesic distance between ({lat1}, {lon1}) and ({lat2}, {lon2}): {e}",
            exc_info=True
        )
        raise ValueError("Geodesic distance calculation failed due to invalid coordinates")
