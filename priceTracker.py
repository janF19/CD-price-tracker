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

# SQLAlchemy setup
Base = declarative_base()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./train_prices.db')

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

# Database engine and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    allow_origins=["*"],  # Allows all origins
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
    
    Parameters:
    - train_code: Filter by specific train code
    - start_date: Filter prices from this date
    - end_date: Filter prices up to this date
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
    Get complete price history for a specific train with comprehensive error handling
    """
    try:
        price_history = db.query(TrainConnection)\
            .filter(TrainConnection.train_code == train_code)\
            .order_by(TrainConnection.scrape_timestamp)\
            .all()
        
        print(f"Price history for {train_code}: {len(price_history)} entries")  # Debug print
        
        if not price_history:
            raise HTTPException(status_code=404, detail=f"No price history found for train {train_code}")
        
        return price_history
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching price history for {train_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
    
    

@app.get("/unique-trains", response_model=List[str])
def get_unique_trains(db: Session = Depends(get_db)):
    """
    Get list of unique train codes with error handling and logging
    """
    try:
        # Use raw SQL to ensure we get distinct train codes
        result = db.execute(text("SELECT DISTINCT train_code FROM train_connections"))
        unique_trains = [row[0] for row in result]
        
        print(f"Unique trains found: {unique_trains}")  # Debug print
        
        if not unique_trains:
            raise HTTPException(status_code=404, detail="No train codes found")
        
        return unique_trains
    except Exception as e:
        print(f"Error fetching unique trains: {e}")  # More detailed error logging
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
    
@app.get("/full-price-history", response_model=List[TrainConnectionResponse])
def get_full_price_history(
    train_code: str = None,  # Optional parameter to filter by specific train
    db: Session = Depends(get_db)
):
    """
    Retrieve full price history for all or specific train(s)
    
    Parameters:
    - train_code: Optional. Filter history for a specific train
    """
    try:
        # Base query for all train connections
        query = db.query(TrainConnection)
        
        # Optional train code filtering
        if train_code:
            query = query.filter(TrainConnection.train_code == train_code)
        
        # Order by timestamp to ensure chronological order
        price_history = query.order_by(TrainConnection.scrape_timestamp).all()
        
        print(f"Full price history retrieved: {len(price_history)} entries")
        
        if not price_history:
            raise HTTPException(status_code=404, detail="No price history found")
        
        return price_history
    except Exception as e:
        print(f"Error retrieving full price history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
    
    
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)