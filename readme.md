# Trend Tracker

A web scraping application that tracks trending topics on X (formerly Twitter) using Python, FastAPI, and Selenium.

## Features
- Automated X.com trend scraping
- Headless browser automation
- MongoDB data storage
- REST API endpoints
- Cookie-based authentication persistence
- IP-based tracking

## Prerequisites
- Python 3.x
- MongoDB
- Chrome browser

## Installation

```bash
# Clone the repository
git clone https://github.com/BhattAnsh/trendTracker.git

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export MONGO_URI="your_mongodb_connection_string"
```

## Usage

```bash
# Start the FastAPI server
uvicorn app:app --reload
```

### Available Endpoints
- `GET /`: Home page with visualization
- `GET /scrape-tweets`: Trigger tweet scraping
- `GET /get-tweets`: Retrieve stored tweets

## Project Structure
```
trendTracker/
├── scrapping/
│   ├── app.py          # Main FastAPI application
│   ├── requirements.txt # Python dependencies
│   ├── cookies.json    # Stored authentication cookies
│   └── templates/      # HTML templates
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
