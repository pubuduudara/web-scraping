from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumService:

    @staticmethod
    def init_web_drive():
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Ensure GUI is off
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Setup WebDriver
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            message = f"An error occurred in init_web_drive: {e}"
            print(message)
