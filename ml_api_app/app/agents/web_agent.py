from app.agents.base_agent import ModelAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.core.utils import read_version_from_cmd 
from webdriver_manager.core.os_manager import PATTERN

from PIL import Image
import io
import base64
import time
import os
import subprocess
from bs4 import BeautifulSoup

class WebAgent(ModelAgent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        preprompt = """You are a web navigation assistant. Your task is to create a plan of action based on the user's prompt and the current state of the web page. 
        When creating a plan, follow these guidelines:
        1. Analyze the current HTML structure and the screenshot provided.
        2. Create a list of steps to accomplish the user's goal.
        3. Each step should be a clear, actionable instruction that can be translated into Selenium code.
        4. Your response should be a numbered list of steps, each on a new line.
        5. Be specific about which elements to interact with (e.g., use IDs, classes, or other attributes).
        6. Consider common web interactions like clicking buttons, filling forms, scrolling, etc.
        7. If the goal requires navigating to different pages, include those steps.
        8. Limit your plan to a maximum of 10 steps for efficiency.

        Example format:
        1. Click the 'Login' button with id 'login-btn'
        2. Enter 'username@example.com' in the input field with name 'email'
        3. Enter 'password123' in the input field with id 'password'
        4. Click the 'Submit' button with class 'submit-btn'
        """
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
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        
        # Specify Chrome binary location (adjust path as needed)
        chrome_binary = "/home/gmartin/chrome-linux64/chrome"
        if os.path.exists(chrome_binary):
            chrome_options.binary_location = chrome_binary
            version = read_version_from_cmd(chrome_binary + "--version", PATTERN["google-chrome"])
            print(f"Chrome binary found at {chrome_binary}.")
        else:
            print(f"Chrome binary not found at {chrome_binary}. Falling back to default.")
        
        try:
            print("Setting up WebDriver")
            service = Service(ChromeDriverManager(driver_version=version).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(800, 600)
            print("WebDriver set up")
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            print(f"Error setting up WebDriver: {str(e)}")
            print(f"Chrome options: {chrome_options.arguments}")
            print(f"Chrome binary location: {chrome_options.binary_location}")
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
        self.current_html = self.clean_html(self.driver.page_source)
        self.current_screenshot = self.take_screenshot()

    def create_plan(self, prompt):
        plan_input = {
            "prompt": prompt,
            "html": self.current_html,
            "screenshot": self.current_screenshot
        }
        print("Plan input: ", plan_input)
        plan_response = self.model.predict(plan_input)
        print("Plan response: ", plan_response)
        self.plan = self.parse_plan(plan_response)

    def execute_step(self, step, prompt):
        step_input = {
            "prompt": prompt,
            "current_step": step,
            "html": self.current_html,
            "screenshot": self.current_screenshot
        }
        print("Step input: ", step_input)
        selenium_code = self.model.predict(step_input)
        print("Selenium code: ", selenium_code)
        
        try:
            exec(selenium_code)
            time.sleep(2)  # Wait for page to load
            self.current_html = self.clean_html(self.driver.page_source)
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

    def clean_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Supprimer les scripts et les styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Conserver uniquement les attributs utiles
        for tag in soup.find_all(True):
            tag.attrs = {key: value for key, value in tag.attrs.items() if key in ['href', 'src', 'id', 'class', 'name', 'type', 'value']}
        
        # Remplacer le contenu textuel par des espaces réservés
        for element in soup.find_all(text=True):
            if element.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                element.replace_with('[TEXT]')
        
        # Retourner la structure HTML nettoyée
        return str(soup)

    def parse_plan(self, plan_response):
        # Split the response into lines and remove any empty lines
        lines = [line.strip() for line in plan_response.split('\n') if line.strip()]
        
        # Parse each line as a step, removing the number at the beginning
        steps = []
        for line in lines:
            # Remove the step number and any leading/trailing whitespace
            step = line.split('.', 1)[-1].strip()
            if step:
                steps.append(step)
        
        return steps

    def parse_verification(self, verification_result):
        # For simplicity, let's assume the model returns "Success" or "Failure"
        return "Success" in verification_result

    def __del__(self):
        if self.driver:
            self.driver.quit()
