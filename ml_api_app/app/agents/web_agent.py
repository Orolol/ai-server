from app.agents.base_agent import ModelAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
import base64
import time
import os
import subprocess

class WebAgent(ModelAgent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        super().__init__(model, memory_db_path, preprompt, system_message)
        print("WebAgent init")
        self.driver = self.setup_webdriver()
        self.current_url = None
        self.current_html = None
        self.current_screenshot = None
        self.plan = []
        self.execution_history = []
        print("WebAgent init done")

    def setup_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")  # Add this line
        
        try:
            # Try to find Chrome binary
            chrome_path = subprocess.check_output(["which", "google-chrome"]).decode().strip()
            chrome_options.binary_location = chrome_path
        except subprocess.CalledProcessError:
            print("Could not find Google Chrome. Make sure it's installed and in your PATH.")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)  # Set page load timeout
            return driver
        except Exception as e:
            print(f"Error setting up WebDriver: {str(e)}")
            # Additional error information
            import sys
            print(f"Python version: {sys.version}")
            print(f"Selenium version: {webdriver.__version__}")
            print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion']}")
            raise

    def act(self, data):
        start_url = data.get("start_url")
        prompt = data.get("prompt")

        self.navigate_to_url(start_url)
        self.create_plan(prompt)
        
        for step in self.plan:
            self.execute_step(step, prompt)

        return self.execution_history

    def navigate_to_url(self, url):
        self.driver.get(url)
        self.current_url = url
        self.current_html = self.driver.page_source
        self.current_screenshot = self.take_screenshot()

    def create_plan(self, prompt):
        plan_input = {
            "prompt": prompt,
            "html": self.current_html,
            "screenshot": self.current_screenshot
        }
        plan_response = self.model.predict(plan_input)
        self.plan = self.parse_plan(plan_response)

    def execute_step(self, step, prompt):
        step_input = {
            "prompt": prompt,
            "current_step": step,
            "html": self.current_html,
            "screenshot": self.current_screenshot
        }
        selenium_code = self.model.predict(step_input)
        
        try:
            exec(selenium_code)
            time.sleep(2)  # Wait for page to load
            self.current_html = self.driver.page_source
            self.current_screenshot = self.take_screenshot()
            
            verification_input = {
                "prompt": prompt,
                "plan": self.plan,
                "current_step": step,
                "screenshot": self.current_screenshot
            }
            verification_result = self.model.predict(verification_input)
            
            if self.parse_verification(verification_result):
                self.execution_history.append({
                    "step": step,
                    "selenium_code": selenium_code,
                    "screenshot": self.current_screenshot,
                    "success": True
                })
            else:
                self.execution_history.append({
                    "step": step,
                    "selenium_code": selenium_code,
                    "screenshot": self.current_screenshot,
                    "success": False
                })
                self.create_plan(prompt)  # Recreate plan if step failed
        except Exception as e:
            self.execution_history.append({
                "step": step,
                "selenium_code": selenium_code,
                "screenshot": self.current_screenshot,
                "success": False,
                "error": str(e)
            })
            self.create_plan(prompt)  # Recreate plan if step failed

    def take_screenshot(self):
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def parse_plan(self, plan_response):
        # Implement parsing logic for the plan
        # This should return a list of steps
        pass

    def parse_verification(self, verification_result):
        # Implement parsing logic for the verification result
        # This should return a boolean indicating success or failure
        pass

    def __del__(self):
        if self.driver:
            self.driver.quit()
