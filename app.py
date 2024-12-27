from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
from dotenv import load_dotenv

app = FastAPI()

# Set up static files and templates for HTML rendering
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB connection

mongo_uri = os.getenv('MONGO_URI', 'fallback_uri')
client = MongoClient(mongo_uri)
db = client["twitter_data"]
collection = db["trends"]

def setup_driver():
    """Set up and return the Selenium WebDriver with headless configuration."""
    options = Options()
    
    # Headless mode configuration
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Set window size for consistent rendering
    options.add_argument("--window-size=1920,1080")
    
    # Additional necessary arguments for stable operation
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Setting user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Browser preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Initialize Chrome driver with binary location
    options.binary_location = "/usr/bin/google-chrome"
    
    try:
        driver = webdriver.Chrome(
            options=options
        )
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"Error creating driver: {str(e)}")
        raise

def save_cookies(driver):
    """Save cookies to a file."""
    cookies = driver.get_cookies()
    with open("cookies.json", 'w') as file:
        json.dump(cookies, file)

def load_cookies(driver):
    """Load cookies from a file if available."""
    if os.path.exists("cookies.json"):
        try:
            with open("cookies.json", 'r') as file:
                cookies = json.load(file)
                driver.get("https://x.com")  # Navigate to the domain first
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Error adding cookie: {e}")
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            print("Invalid or corrupted cookies file. Login required.")
    return False

def is_logged_in(driver):
    """Check if the user is logged in by looking for a specific element."""
    try:
        driver.get("https://x.com/home")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Timeline: Your Home Timeline"]'))
        )
        return True
    except Exception:
        return False

def login_and_get_cookies(driver):
    """Perform login and save cookies."""
    try:
        driver.get("https://x.com/i/flow/login")
        time.sleep(5)

        # Enter username with explicit wait
        username = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]'))
        )
        email = os.environ("EMAIL")
        username.send_keys(email)
        
        nextButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@role="button"]//span[text()="Next"]'))
        )
        nextButton.click()
        time.sleep(3)

        # Handle optional authentication
        try:
            authInput = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@inputmode="text"]'))
            )
            username = os.environ("USERNAME")
            authInput.send_keys(username)
            nextButton = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@role="button"]//span[text()="Next"]'))
            )
            nextButton.click()
            time.sleep(3)
        except:
            print("Authentication step not required.")

        # Enter password with explicit wait
        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]'))
        )
        pswd = os.environ("PASSWORD")
        password.send_keys(pswd)
        
        loginButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
        )
        loginButton.click()
        time.sleep(3)

        # Save cookies after successful login
        save_cookies(driver)
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment."""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/get-tweets")
async def get_past_tweets():
    """Fetch past tweets grouped by IP address."""
    try:
        data = list(collection.find({}, {"_id": 0, "ip_address": 1, "tweets": 1}))
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching past tweets: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Renders the home page with buttons."""
    data = list(collection.find({}, {"_id": 0}))
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

@app.get("/scrape-tweets")
async def scrape_tweets(request: Request):
    """Endpoint to scrape tweets."""
    driver = setup_driver()
    client_ip = request.client.host

    try:
        if not load_cookies(driver):
            login_and_get_cookies(driver)

        if not is_logged_in(driver):
            raise HTTPException(status_code=401, detail="Login failed. Please try again.")

        driver.get("https://x.com/explore/tabs/for-you")
        time.sleep(5)

        # Use WebDriverWait for more reliable scraping
        tweets = []
        for i in range(1, 6):
            try:
                tweet_text = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        f'/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[{i}]/div/div/div/div/div[2]/span'
                    ))
                ).text
                tweets.append({"tweet_number": i, "text": tweet_text})
            except Exception as e:
                print(f"Error scraping tweet {i}: {e}")

        collection.insert_one({"ip_address": client_ip, "tweets": tweets, "timestamp": time.time()})
        return {"status": "success", "tweets": tweets}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
    finally:
        driver.quit()
