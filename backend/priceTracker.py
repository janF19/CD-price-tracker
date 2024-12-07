import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uvicorn
from scrape import automate_train_search  # Your existing scraper
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from dotenv import load_dotenv
import psycopg2
import traceback
import os
import psycopg2
from urllib.parse import urlparse, quote_plus
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus



# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get the DATABASE_URL
# Manually parse the DATABASE_URL


# Load environment variables
load_dotenv()

# Database connection URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Create Base and engine
Base = declarative_base()
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={'options': '-c client_encoding=utf8'}
)

# Create SessionLocal 
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)

# Define SQLAlchemy Model
class TrainConnection(Base):
    __tablename__ = "train_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    train_code = Column(String, index=True)
    departure_time = Column(String)
    departure_station = Column(String)
    price = Column(Float)
    scrape_timestamp = Column(DateTime, default=datetime.utcnow)

# Pydantic model for API responses
class TrainConnectionResponse(BaseModel):
    id: int
    train_code: str
    departure_time: str
    departure_station: str
    price: float
    scrape_timestamp: datetime

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI application
app = FastAPI(title="Train Price Tracker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scheduler Integration
class TrainPriceTracker:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def save_connections_to_db(self, connections):
        if not connections:
            print("No connections to save.")
            return

        timestamp = datetime.now()
        with self.SessionLocal() as session:
            for connection in connections:
                train_connection = TrainConnection(
                    train_code=connection.get('Train Code', 'N/A'),
                    departure_time=connection.get('Departure Time', 'N/A'),
                    departure_station=connection.get('Departure Station', 'N/A'),
                    price=float(connection.get('Price', 0)),
                    scrape_timestamp=timestamp
                )
                session.add(train_connection)
            session.commit()
        print(f"Saved {len(connections)} connections to database")

    def run_scrape_and_save(self):
        try:
            connections = automate_train_search()
            print(f"Connections retrieved: {len(connections)}")
            
            if connections:
                self.save_connections_to_db(connections)
            else:
                print("No connections retrieved from scraping.")
        except Exception as e:
            print(f"Error in scraping and saving: {e}")

    def start_scheduler(self):
        scheduler = BlockingScheduler()
        
        # Run immediately once
        self.run_scrape_and_save()
        
        # Then schedule subsequent runs
        scheduler.add_job(self.run_scrape_and_save, 'interval', hours=24)
        
        try:
            print("Scheduler started. Press Ctrl+C to exit.")
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\nScheduler stopped.")

# Start scheduler in a separate thread
def start_scheduler_thread():
    tracker = TrainPriceTracker()
    scheduler_thread = Thread(target=tracker.start_scheduler)
    scheduler_thread.start()

@app.on_event("startup")
async def startup_event():
    start_scheduler_thread()

@app.get("/train-prices", response_model=List[TrainConnectionResponse])
def get_train_prices(
    train_code: str = None, 
    start_date: datetime = None, 
    end_date: datetime = None, 
    db: Session = Depends(get_db)
):
    """
    Retrieve train prices with optional filtering
    """
    query = db.query(TrainConnection)
    
    if train_code:
        query = query.filter(TrainConnection.train_code == train_code)
    
    if start_date:
        query = query.filter(TrainConnection.scrape_timestamp >= start_date)
    
    if end_date:
        query = query.filter(TrainConnection.scrape_timestamp <= end_date)
    
    return query.order_by(TrainConnection.scrape_timestamp).all()

@app.get("/price-history/{train_code}", response_model=List[TrainConnectionResponse])
def get_price_history_for_train(train_code: str, db: Session = Depends(get_db)):
    """
    Get complete price history for a specific train
    """
    price_history = db.query(TrainConnection)\
        .filter(TrainConnection.train_code == train_code)\
        .order_by(TrainConnection.scrape_timestamp)\
        .all()
    
    if not price_history:
        raise HTTPException(status_code=404, detail=f"No price history found for train {train_code}")
    
    return price_history

@app.get("/unique-trains", response_model=List[str])
def get_unique_trains(db: Session = Depends(get_db)):
    """
    Get list of unique train codes
    """
    result = db.execute(text("SELECT DISTINCT train_code FROM train_connections"))
    unique_trains = [row[0] for row in result]
    
    if not unique_trains:
        raise HTTPException(status_code=404, detail="No train codes found")
    
    return unique_trains

@app.get("/full-price-history", response_model=List[TrainConnectionResponse])
def get_full_price_history(
    train_code: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve full price history for all or specific train(s)
    """
    query = db.query(TrainConnection)
    
    if train_code:
        query = query.filter(TrainConnection.train_code == train_code)
    
    price_history = query.order_by(TrainConnection.scrape_timestamp).all()
    
    if not price_history:
        raise HTTPException(status_code=404, detail="No price history found")
    
    return price_history


if __name__ == "__main__":
    # Get the dynamic port assigned by Render (default to 8000 if missing for local development)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)