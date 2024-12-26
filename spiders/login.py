
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import json


class Login:
    def __init__(self, username, password):
        self.name = username
        self.password = password
        self.driver = Webdriver().driver
        self.driver.maximize_window()

    def navigate_to_website(self):
        self. driver.get("https://x.com/i/flow/login")
        time.sleep(5)

    def username_form(self):
        username = self.driver.find_element(
            By.XPATH, '//input[@autocomplete="username"]')
        username.send_keys(self.username)
        time.sleep(5)

    def auth_form(self):
        authInput = self.driver.find_element(
            By.XPATH, '//input[@inputmode="text"]')
        authInput.send_keys("AnshBhatt553446")
        time.sleep(3)

    def password_form(self):
        password = self.driver.find_element(
            By.XPATH, '//input[@autocomplete="current-password"]')
        password.send_keys("Ansh@1234")

    def next_button(self):
        nextButton = self.find_element(
            By.XPATH, '//button[@role="button"]//span[text()="Next"]')
        nextButton.click()

    def login_button(self):
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
            )
        button.click()

    def save_cookies(self):
        time.sleep(9)
        cookies = self.driver.get_cookies()
        with open("cookies_x.json", "w") as file:
            json.dump(cookies, file)

    def exec(self):
        self.navigate_to_website()
        self.username_form()
        self.next_button()
        self.auth_form()
        self.next_button()
        self.password_form()
        self.login_button()
        self.save_cookies()
