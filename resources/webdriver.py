from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Webdriver:
    def __init__(self):  # keep headless false for debugging and checking it
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        prefs = {
            "download.default_directory": "./",
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "excludeSwitches": ["disable-popup-blocking"]
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
