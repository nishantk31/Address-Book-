import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db

# Configure isolated, thread-safe SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Dependency override injection for in-memory sessioning."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply overrides globally to the FastAPI app under test
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    """Drops and recreates schemas before every unit test block to ensure total isolation."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check() -> None:
    """Verifies that the /health endpoint is operational and returns standard content."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_address_success() -> None:
    """Verifies that a valid address payload is accepted and successfully persisted."""
    payload = {
        "name": "Home Office",
        "street": "100 MG Road",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5204,
        "longitude": 73.8567
    }
    response = client.post("/api/v1/addresses/", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Home Office"
    assert data["street"] == "100 MG Road"
    assert data["city"] == "Pune"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_address_validation_error_coords() -> None:
    """Asserts that latitude coordinates exceeding standard constraints fail validation."""
    payload = {
        "name": "Out of Bounds",
        "street": "Space Center",
        "city": "Orbit City",
        "state": "Atmosphere",
        "country": "Exoplanet",
        "latitude": 98.432,  # Invalid latitude (> 90.0)
        "longitude": 73.8567
    }
    response = client.post("/api/v1/addresses/", json=payload)
    assert response.status_code == 422
    
    errors = response.json().get("errors", [])
    assert any("latitude" in err["field"] for err in errors)

def test_create_address_validation_error_whitespace() -> None:
    """Asserts that empty or whitespace-only inputs trigger validation failures."""
    payload = {
        "name": "   ",  # Whitespace only
        "street": "Main Street",
        "city": "Vegas",
        "state": "NV",
        "country": "USA",
        "latitude": 36.1699,
        "longitude": -115.1398
    }
    response = client.post("/api/v1/addresses/", json=payload)
    assert response.status_code == 422
    
    errors = response.json().get("errors", [])
    assert any("name" in err["field"] for err in errors)

def test_get_address_not_found() -> None:
    """Asserts that requests for non-existent IDs gracefully return a 404 error."""
    response = client.get("/api/v1/addresses/999")
    assert response.status_code == 404
    assert "ID 999 was not found" in response.json()["detail"]

def test_update_address_patch_behavior() -> None:
    """Verifies that patch (PUT) operations only modify specified properties."""
    # Create seed record
    payload = {
        "name": "HQ",
        "street": "Sector 1",
        "city": "Noida",
        "state": "UP",
        "country": "India",
        "latitude": 28.5355,
        "longitude": 77.3910
    }
    created = client.post("/api/v1/addresses/", json=payload).json()
    addr_id = created["id"]

    # Partial update: modify only name and street
    update_payload = {
        "name": "New HQ",
        "street": "Sector 5"
    }
    response = client.put(f"/api/v1/addresses/{addr_id}", json=update_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "New HQ"
    assert data["street"] == "Sector 5"
    # Unmodified fields should remain the same
    assert data["city"] == "Noida"
    assert data["latitude"] == 28.5355

def test_delete_address_lifecycle() -> None:
    """Tests the deletion of an address and verifies it can no longer be accessed."""
    payload = {
        "name": "Delete Me",
        "street": "Temporary Lane",
        "city": "Disappearing City",
        "state": "State",
        "country": "Country",
        "latitude": 0.0,
        "longitude": 0.0
    }
    created = client.post("/api/v1/addresses/", json=payload).json()
    addr_id = created["id"]

    # Delete the record
    delete_response = client.delete(f"/api/v1/addresses/{addr_id}")
    assert delete_response.status_code == 204

    # Verify lookups now return a 404
    lookup_response = client.get(f"/api/v1/addresses/{addr_id}")
    assert lookup_response.status_code == 404

def test_nearby_distance_search_geodesic() -> None:
    """
    Tests geodesic distance boundary filtering.
    Seeds multiple Pune markers and queries them with precise kilometer radii.
    """
    # Seed 3 markers:
    # 1. Shaniwar Wada (Pune Center)
    # 2. Dagadusheth Temple (~0.33 km from Wada)
    # 3. Hinjewadi Phase 1 (~14.8 km from Wada)
    p1 = {
        "name": "Shaniwar Wada",
        "street": "Shaniwar Peth",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5193,
        "longitude": 73.8553
    }
    p2 = {
        "name": "Dagadusheth Temple",
        "street": "Budhwar Peth",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5164,
        "longitude": 73.8561
    }
    p3 = {
        "name": "Hinjewadi IT Park",
        "street": "Hinjewadi Phase 1",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5913,
        "longitude": 73.7382
    }

    client.post("/api/v1/addresses/", json=p1)
    client.post("/api/v1/addresses/", json=p2)
    client.post("/api/v1/addresses/", json=p3)

    # Query with Shaniwar Wada coords and radius=2.0 km
    # Expect: Wada (0.0km) and Dagadusheth (~0.33km), but NOT Hinjewadi
    response = client.get(
        "/api/v1/addresses/nearby",
        params={"latitude": 18.5193, "longitude": 73.8553, "distance_km": 2.0}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    
    # Assert proper sorting (nearest first)
    assert results[0]["name"] == "Shaniwar Wada"
    assert results[0]["distance_km"] == 0.0
    
    assert results[1]["name"] == "Dagadusheth Temple"
    assert 0.3 < results[1]["distance_km"] < 0.4
