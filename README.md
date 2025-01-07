# CD Price Tracker 📈

A web application that tracks and visualizes price changes for trains running between Prague and Ostrava Svinov on the Czech Railways (České dráhy) network. The system performs automated price scraping twice daily to analyze how train ticket prices fluctuate over time, providing insights into pricing patterns and variations between different trains and weeks.

## Overview 🚂

This project monitors train ticket prices specifically for Friday departures from Prague to Ostrava Svinov after 13:20. By collecting price data twice daily (8 AM and 6 PM) starting one week before each Friday, the application enables users to:
- Observe price fluctuations over time
- Compare pricing patterns between different trains
- Analyze week-to-week variations in pricing strategies
- Identify trains with more frequent price changes

The analysis follows a "ceteris paribus" approach, focusing solely on price changes over time without accounting for factors like train capacity.

## Features ✨

### Backend
- Automated web scraping of České dráhy (CD) website twice daily
- RESTful API endpoints for retrieving price history
- PostgreSQL database for storing historical price data
- Scheduled tasks using APScheduler
- FastAPI framework for efficient API handling

### Frontend
- Interactive charts for visualizing price trends
- Train-specific price history visualization
- User-friendly interface for selecting specific trains
- Real-time data updates
- Responsive design for various screen sizes

## Tech Stack 🛠

- **Backend**:
  - FastAPI
  - SQLAlchemy
  - APScheduler
  - Python Web Scraping Tools
  - PostgreSQL
  - uvicorn

- **Frontend**:
  - React
  - Axios for API communication
  - Chart visualization libraries
  - CSS for styling

## Setup and Installation 🚀

### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL database
- Git

### Backend Setup
1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd [repo-name]
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database_name]
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## API Endpoints 🌐

- `GET /train-prices` - Retrieve train prices with optional filtering
- `GET /price-history/{train_code}` - Get price history for a specific train
- `GET /unique-trains` - Get list of all unique train codes
- `GET /full-price-history` - Retrieve complete price history

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.
