import calendar

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, \
    ElementNotInteractableException
import time, requests, pytesseract, json, platform, os
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from datetime import date, datetime
from dotenv import load_dotenv

from supabase_connection import get_supabase_client, insert_leads_v2

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Your OpenAI API client initialization
client = OpenAI(api_key=OPENAI_API_KEY)

class Main:
    def __init__(self):
        print("Running Cleaveland Foreclosure Bot Scraper")
        self.supabase = get_supabase_client()

    def run(self):
        try:

            # 1. Configure headless mode for a server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 2. Automatically download and install the correct chromedriver
            # This works for both Ubuntu and macOS
            service = ChromeService(ChromeDriverManager().install())

            # 3. Initialize the WebDriver with the service and options
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)

            # ... (rest of your scraping logic)
            driver.get("https://cpdocket.cp.cuyahogacounty.gov/Search.aspx")

            wait.until(EC.presence_of_element_located((By.ID, "form1")))

            wait.until(EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_rbCivilForeclosure"))).click()
            time.sleep(3)

            wait.until(EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_btnYes"))).click()
            time.sleep(3)

            wait.until(EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_rbCivilForeclosure"))).click()
            time.sleep(3)

            today = date.today()

            # Get the first day of the current month
            start_date_str = today.replace(day=1).strftime("%m/%d/%Y")

            # Get the last day of the current month
            # First, find the number of days in the current month
            last_day_of_month = calendar.monthrange(today.year, today.month)[1]
            end_date_str = today.replace(day=last_day_of_month).strftime("%m/%d/%Y")

            # Find the start date input field and set its value using JavaScript
            start_date_input = driver.find_element(By.ID, "SheetContentPlaceHolder_foreclosureSearch_txtFromDate")
            driver.execute_script("arguments[0].value = arguments[1];", start_date_input, start_date_str)

            # Find the end date input field and set its value using JavaScript
            end_date_input = driver.find_element(By.ID, "SheetContentPlaceHolder_foreclosureSearch_txtToDate")
            driver.execute_script("arguments[0].value = arguments[1];", end_date_input, end_date_str)

            wait.until(EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_foreclosureSearch_btnSubmit"))).click()
            time.sleep(10)

            results = driver.find_element(By.ID, "SheetContentPlaceHolder_ctl00_gvForeclosureResults").find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
            for result in results[1:]:
                tds = result.find_elements(By.TAG_NAME, "td")
                defendant = tds[0].text
                address = tds[1].text
                city = tds[2].text
                zip = tds[3].text
                case_number = tds[4].text
                parcel_number = tds[5].text
                status = tds[6].text
                file_date = datetime.strptime(tds[7].text, "%m/%d/%Y").date()



                response = self.supabase.table('foreclosure_leads_v2').select("*").eq('type', 'cleaveland').eq('document_id', case_number).execute()
                data = response.data

                if data:
                    print(f"Case {case_number} found!")
                else:
                    new_lead = insert_leads_v2(
                        address=address,
                        city=city,
                        state="Ohio",
                        zip=zip,
                        workflow=1,
                        document_url="",
                        document_id=case_number,
                        file_date=file_date,
                        sale_date=date.today(),
                        table="foreclosure_leads_v2",
                        type="cleaveland",
                        name="defendant"
                    )
                    print("✅ Inserted:", new_lead)


        except Exception as e:
            print("❌ Error:", e)


if __name__ == "__main__":
    main = Main()
    # main.scrape_via_soup("CV-2025-09-4147")
    main.run()
    # main.scrape_via_workflow2(5604009)