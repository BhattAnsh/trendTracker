from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    prefs = {
        "download.default_directory": "./",
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "excludeSwitches": ["disable-popup-blocking"]
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def login_and_get_cookies(driver):
    driver.get("https://x.com/i/flow/login")
    time.sleep(5)

    # Enter username
    username = driver.find_element(By.XPATH, '//input[@autocomplete="username"]')
    email = os.environ("EMAIL")
    username.send_keys(email)
    nextButton = driver.find_element(By.XPATH, '//button[@role="button"]//span[text()="Next"]')
    nextButton.click()
    time.sleep(5)

    # Handle optional authentication
    try:
        authInput = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[@inputmode="text"]'))
        )
        username = os.environ("USERNAME")
        authInput.send_keys(username)
        nextButton = driver.find_element(By.XPATH, '//button[@role="button"]//span[text()="Next"]')
        nextButton.click()
        time.sleep(5)
    except:
        print("Authentication step not required.")

    # Enter password
    password = driver.find_element(By.XPATH, '//input[@autocomplete="current-password"]')
    pswd = os.environ("PASSWORD")
    password.send_keys(pswd)
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
    )
    button.click()
    time.sleep(3)

    # Save cookies
    cookies = driver.get_cookies()
    with open("cookies.json", 'w') as file:
        json.dump(cookies, file)
    return cookies

def load_cookies(driver):
    try:
        with open("cookies.json", 'r') as file:
            cookies = json.load(file)
            # First, go to the domain for which the cookies were created
            driver.get("https://x.com")
            # Add the cookies to the current session
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {e}")
            return True
    except FileNotFoundError:
        print("No cookies file found")
        return False
    except json.JSONDecodeError:
        print("Invalid cookies file")
        return False

def scrape_tweets():
    driver = setup_driver()

    try:
        # Try to load cookies first
        if not load_cookies(driver):
            # If no valid cookies, perform login
            login_and_get_cookies(driver)

        # Navigate to the explore page
        driver.get("https://x.com/explore/tabs/for-you")
        driver.maximize_window()
        time.sleep(5)

        # Scrape tweets
        for i in range(1, 6):
            try:
                text = driver.find_element(
                    By.XPATH, f'/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/section/div/div/div[{i}]/div/div/div/div/div[2]/span'
                ).text
                print(text)
            except Exception as e:
                print(f"Error scraping tweet {i}: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_tweets()
