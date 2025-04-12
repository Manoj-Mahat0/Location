from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware



# Database setup
DATABASE_URL = "sqlite:///./test.db"  # SQLite database for testing; you can change to other databases like PostgreSQL, MySQL

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Database models
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Define a model to validate incoming location data
class LocationData(BaseModel):
    latitude: float
    longitude: float
    timestamp: str

    @validator('timestamp')
    def validate_timestamp(cls, v):
        # Ensure the timestamp is in ISO 8601 format with a 'Z' for UTC
        try:
            # Convert the timestamp string to a datetime object, handling the 'Z' at the end
            return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format. Error: {e}")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to receive location updates via HTTP POST
@app.post("/update-location")
async def update_location(location_data: LocationData, db: Session = Depends(get_db)):
    try:
        # Log the received data (in a real app, you'd store this in a database)
        new_location = Location(
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timestamp=location_data.timestamp
        )
        
        db.add(new_location)
        db.commit()
        db.refresh(new_location)

        # Return a successful response
        return {"message": "Location received successfully", "data": location_data}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to retrieve the latest location data from the database
@app.get("/latest-location")
async def get_latest_location(db: Session = Depends(get_db)):
    try:
        location = db.query(Location).order_by(Location.timestamp.desc()).first()
        if location is None:
            raise HTTPException(status_code=404, detail="No location data found")
        return {"latitude": location.latitude, "longitude": location.longitude, "timestamp": location.timestamp.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
