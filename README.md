# Address Book REST API

A production-ready, highly-polished FastAPI Address Book REST API with database persistence, coordinates boundary validation, robust logging, isolated testing, and oblate-spheroid geodesic distance calculations using the `geopy` library.

---

## 🚀 Key Features & Highlights

- **Clean Layered Architecture**: Clear separation of concerns (Routers -> Services -> Models -> Database).
- **Geodesic Distance Queries**: Leverages the oblate-spheroid WGS-84 model via `geopy` for millimeter-accurate distance search (avoiding manual, buggy Haversine estimations).
- **Strict Boundary Validation**: Uses Pydantic V2 `@field_validator` hooks to strip inputs, check latitude bounds ([-90.0, 90.0]), longitude bounds ([-180.0, 180.0]), and prevent empty or whitespace-only strings.
- **Global Error Management**: Intercepts Pydantic boundary validation errors, database integrity failures, and runtime exceptions globally, returning unified JSON structures.
- **Production-grade Logging**: Standard library logging configured with high-detail timestamps, severity levels, and execution file markers.
- **Automated Database Bootstrapping**: Initializes SQLite schema automatically on startup inside an async lifespan context.
- **Docker Containerization**: Full Docker and Docker Compose integrations included for instant deployment.
- **Robust Isolated Tests**: Comprehensive suite running on thread-isolated in-memory SQLite instances (`sqlite:///:memory:` with `StaticPool`).

---

## 🛠 Tech Stack

- **Core**: Python 3.11+
- **Framework**: FastAPI
- **Web Server**: Uvicorn
- **ORM & Database**: SQLAlchemy & SQLite
- **Math / Geolocation**: geopy (geodesic distance)
- **Validation**: Pydantic v2
- **Config Loader**: pydantic-settings
- **Unit Tests**: pytest & httpx
- **Containerization**: Docker & Docker Compose

---

## 📂 Project Structure

```text
address-book-api/
│
├── app/
│   ├── main.py                  # API application bootstrap & lifespan
│   ├── core/
│   │   └── config.py            # Environment validation & settings loader
│   ├── database/
│   │   ├── connection.py        # SQLite engine, sessions & dependency provider
│   │   └── models.py            # SQLAlchemy Address data model
│   ├── routes/
│   │   └── address_routes.py    # Address endpoints (POST, GET, PUT, DELETE, GET nearby)
│   ├── schemas/
│   │   └── address_schema.py    # Pydantic validation schemas
│   ├── services/
│   │   └── address_service.py   # Database query orchestration & distance sorting
│   ├── utils/
│   │   ├── logger.py            # Console output formatter
│   │   └── geo.py               # geopy distance calculation wrapper
│   └── exceptions/
│       └── handlers.py          # Unified exception responses
│
├── tests/
│   └── test_address.py          # Isolated tests
│
├── .env                         # Local configuration variables
├── .gitignore                   # Version control exclusions
├── Dockerfile                   # Deployment container blueprint
├── docker-compose.yml           # Multi-service coordinator
├── requirements.txt             # Dependency manifest
├── README.md                    # Setup & documentation
├── pytest.ini                   # Pytest path settings
└── address_book.db              # Auto-generated SQLite database (git ignored)
```

---

## ⏱ 5-Minute Quickstart

### Method 1: Local Setup

1. **Clone the Repository & Navigate**
   ```bash
   git clone <repository_url>
   cd address-book-app
   ```

2. **Establish a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Environment Variables**
   The application loads defaults, but you can customize them by looking at `.env`:
   ```bash
   cat .env
   ```

5. **Start the Application**
   ```bash
   uvicorn app.main:app --reload
   ```
   *The API will be available at: [http://localhost:8000](http://localhost:8000)*  
   *Interactive API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### Method 2: Docker Compose Setup

Run the entire application in a containerized environment with a single command:
```bash
docker-compose up --build
```
*Port `8000` is forwarded from the container to your host system.*

---

## 🧪 Running Unit Tests

Our unit test suite runs in absolute isolation against an in-memory SQLite database, verifying all validations, status codes, and geodesic algorithms.

Run the tests inside your virtual environment:
```bash
pytest -v
```

---

## 📝 API Endpoints

### 1. Health Status
- **Method**: `GET`
- **Path**: `/health`
- **Description**: Returns 200 OK if service is online.
- **Response**:
  ```json
  {"status": "healthy"}
  ```

---

### 2. Create Address
- **Method**: `POST`
- **Path**: `/api/v1/addresses`
- **Description**: Creates a new contact address.
- **Request Payload**:
  ```json
  {
    "name": "Central Office",
    "street": "MG Road",
    "city": "Pune",
    "state": "Maharashtra",
    "country": "India",
    "latitude": 18.5204,
    "longitude": 73.8567
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": 1,
    "name": "Central Office",
    "street": "MG Road",
    "city": "Pune",
    "state": "Maharashtra",
    "country": "India",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "created_at": "2026-05-24T12:00:00Z",
    "updated_at": "2026-05-24T12:00:00Z"
  }
  ```

---

### 3. Get All Addresses (Paginated)
- **Method**: `GET`
- **Path**: `/api/v1/addresses`
- **Query Params**:
  - `page`: Page number (default: `1`, minimum: `1`)
  - `limit`: Records per page (default: `10`, maximum: `100`)
- **Response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "name": "Central Office",
      ...
    }
  ]
  ```

---

### 4. Update Address (Patching Semantics)
- **Method**: `PUT`
- **Path**: `/api/v1/addresses/{id}`
- **Description**: Updates specified fields of an address.
- **Request Payload**:
  ```json
  {
    "name": "Sweet Home",
    "street": "Aundh Road"
  }
  ```
- **Response (200 OK)**: Returns the updated address object.

---

### 5. Find Nearby Addresses
- **Method**: `GET`
- **Path**: `/api/v1/addresses/nearby`
- **Description**: Finds addresses within a kilometer radius from a coordinate, sorted nearest first.
- **Query Params**:
  - `latitude`: Search center latitude (e.g., `18.5193`)
  - `longitude`: Search center longitude (e.g., `73.8553`)
  - `distance_km`: Radius in kilometers (e.g., `5.0`)
- **Response (200 OK)**:
  ```json
  [
    {
      "id": 2,
      "name": "Dagadusheth Temple",
      "street": "Shivaji Road",
      "city": "Pune",
      "state": "Maharashtra",
      "country": "India",
      "latitude": 18.5164,
      "longitude": 73.8561,
      "created_at": "2026-05-24T12:00:00Z",
      "updated_at": "2026-05-24T12:00:00Z",
      "distance_km": 0.3341
    }
  ]
  ```

---

### 6. Delete Address
- **Method**: `DELETE`
- **Path**: `/api/v1/addresses/{id}`
- **Response (204 No Content)**: The resource was deleted.

---

## 🛡 Boundary Error Response Example
If coordinate parameters fail validation:
- **Status Code**: `422 Unprocessable Entity`
- **Response Body**:
  ```json
  {
    "detail": "Validation error at boundary",
    "errors": [
      {
        "field": "body -> latitude",
        "message": "Value error, Latitude must be between -90.0 and 90.0 degrees"
      }
    ]
  }
  ```
