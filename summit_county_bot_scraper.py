from datetime import date
from openai import OpenAI
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, \
    ElementNotInteractableException
import time, requests, pytesseract, json

# Note: The webdriver_manager library is no longer needed since you are using a
# manually installed chromedriver.
# from webdriver_manager.chrome import ChromeDriverManager

# Your OpenAI API client initialization
client = OpenAI(api_key="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")

class Main:
    def __init__(self):
        print("Running Harris Bot Scraper")

    def run(self):
        try:
            # 1. Configure headless mode for a server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 2. Specify the path to your manually installed chromedriver
            chromedriver_path = '/usr/bin/chromedriver'
            service = ChromeService(executable_path=chromedriver_path)

            # 3. Initialize the WebDriver with the service and options
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)

            driver.get("https://clerkweb.summitoh.net/Welcome.asp")

            record_search_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/table/tbody/tr[3]/td[2]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/a[1]")))
            driver.execute_script("arguments[0].click();", record_search_btn)
            time.sleep(1)

            agree_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/table[2]/tbody/tr[2]/td/center/p[1]/a")))
            driver.execute_script("arguments[0].click();", agree_btn)
            time.sleep(1)

            civil_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/font/table[1]/tbody/tr[2]/td/a")))
            driver.execute_script("arguments[0].click();", civil_btn)
            time.sleep(1)

            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                "/html/body/table[2]/tbody/tr[1]/td/form/center/div/div/center/table/tbody/tr/td/table/tbody/tr[5]/td/a")))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(1)

            today = date.today()

            # Format as MM/YYYY
            formatted = today.strftime("%m/%Y")

            case_month_input = wait.until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_tbFilingMonth")))
            case_month_input.send_keys(formatted)
            time.sleep(1)

            judge_select = wait.until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_drpJudgeName")))
            Select(judge_select).select_by_visible_text("ADAMS, JASON")
            time.sleep(1)

            case_type = wait.until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_drpCaseType")))
            Select(case_type).select_by_visible_text("Foreclosure")
            time.sleep(1)

            wait.until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_btnSearch"))).click()
            time.sleep(5)

            wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblSelection")))

            if 'No Entries Found. .' not in driver.page_source:
                trs = driver.find_element(By.ID, "ContentPlaceHolder1_gvMixedResults").find_elements(By.TAG_NAME, "tr")
                for tr in trs[1:]:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    filing_date = tds[0].text
                    case_number_element = tds[1]
                    case_number = case_number_element.text
                    caption = tds[2].text

                    data = self.scrape_via_soup(case_number)
                    if data and 'found' in data and data['found'] == False:
                        parcel_number = data['parcel_number']

        except Exception as e:
            print("❌ Error:", e)

    def scrape_via_soup(self, case_number):
        try:
            url = f"https://clerkweb.summitoh.net/PublicSite/CaseDetail.aspx?CaseNo={case_number}&Suffix=&Type="

            # The headers and payload remain the same
            payload = {}
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'Cookie': 'ASPSESSIONIDCAXRRRDR=JPAJLNHDLDDMMFMNCPOBLJDN; ASP.NET_SessionId=250pifexbjd0i0qu1vs21hqd; ASPSESSIONIDCETRRRDR=KBCJLNHDHPLCKLIEMEOOBELF; ASPSESSIONIDAEQRSQDR=EAECANLDLBLIDDHBIBGLBJPC; ASPSESSIONIDAAURSQDR=FLECANLDGAAHMPCAHLJEPKFO; ASPSESSIONIDAETQSSBQ=COLFEMPDHDOLHMAGNEPAPIFM; ASPSESSIONIDAAXQSSBQ=PPMIEMPDOBCNBKGOFJOEANAO'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            print(f"Scraping: {url} | Case Number: {case_number} | Status: {response.status_code}")
            if not response.ok:
                print("❌ Failed to fetch page", url)

            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.select("#ContentPlaceHolder1_igtabCaseDetails__ctl1_gvDocketDetails tr")
            for row in rows:
                row_tds = row.find_all("td")
                if row_tds:
                    docket_text = row_tds[2].text
                    if "FORECLOSURE COMPLAINT" in docket_text:
                        document_element = row_tds[3].find("a")
                        if document_element and document_element.has_attr("href"):
                            href_value = document_element["href"]
                            document_url = f"https://clerkweb.summitoh.net/PublicSite/{href_value}"
                            data = self.download_and_analyze_pdf(document_url)
                            if data and '```json' in data:
                                data = data.replace('```json', '').replace('```', '')

                            data = json.loads(data)
                            return data

                        else:
                            print("No <a> tag or href found.")
            return None
        except Exception as e:
            print(f"Error while scraping via soup: {case_number} | {str(e)}")
            return None

    def scrape_via_workflow2(self, parcel_number):
        try:
            # 1. Configure headless mode for a server environment
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 2. Specify the path to your manually installed chromedriver
            chromedriver_path = '/usr/bin/chromedriver'
            service = ChromeService(executable_path=chromedriver_path)

            # 3. Initialize the WebDriver with the service and options
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)

            driver.get(
                "[https://propertyaccess.summitoh.net/search/commonsearch.aspx?mode=realprop](https://propertyaccess.summitoh.net/search/commonsearch.aspx?mode=realprop)")

            wait.until(EC.presence_of_element_located((By.ID, "btAgree"))).click()
            time.sleep(2)

            search_box = wait.until(EC.presence_of_element_located((By.ID, "inpParid")))
            search_box.send_keys(parcel_number)

            wait.until(EC.element_to_be_clickable((By.ID, "btSearch"))).click()
            time.sleep(3)

            results = driver.find_elements(By.ID, "searchResults")
            if results:
                result = results[-1].click()
                address = driver.find_elements(By.XPATH,
                                               "/html/body/div/div[3]/section/div/main/form/div[3]/div/div/table/tbody/tr/td/table/tbody/tr[2]/td/div/div[1]/table[2]/tbody/tr[2]/td[2]")
                if address:
                    address = address[0]
                    address = address.text
                    print(address)

        except Exception as e:
            print(f"Error while running scraper for workflow #2: {str(e)}")

    def download_and_analyze_pdf(self, document_url, filename="document.pdf"):
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=MBMCDAPNEAMCDBPEOCFFAMKLMAGKHNIAGCCGKNMIDHGLNBBINFLPJGLDMOPMLFPOPGHDEFAIOJPAIAJLMIPAIKHEGBFHEGKOMOKGMGPPNFLLGMPJMMHGDDJPBJMNOLJK; ASP.NET_SessionId=ngtuag543l01m4xfpwad1pur; f5avraaaaaaaaaaaaaaaa_session_=EPKMNLANHDJMCGGEDAKHGBFEGHKHNILOKDINNLLNOCIDOEJDLBGNDENKHJBFPGILCMADCBDJJCFPCIIEPOEABLOHOPEJHFGKADJNPEKNHDAFHJNHMEKPIIKABMGBCOIG; ajs_anonymous_id=%226d76ea9e-7d5e-4127-85a0-e511ad57ec8d%22; .ASPXAUTH=2A2A38541596F51F82EFEB344338FB0CA3AD9FF511B664866DAE6D906BFFE39804CEFA9BF5165131C66032EFE043357383722F43553271267F0A6FB998708EBB1C7AD134C827FA4FFBB7B31B70AC9679448CD2050740BE7D57B7228AF13323C3CD0BD187E9F6091CE825AA529415F4137568553AF8837EA1FB14FB5555312E95C6B2E7FD0648D3088184187E473625FB; f5avraaaaaaaaaaaaaaaa_session_=NCHOIFMECKECJPOMEONFJIGNDMOGBNCLEOKIDEMNNOOPMLIMLBMGADFAFGIGJNEAPCADKBLMJGKNPLFLKPKAKCKNCAIGMGHELLLOPIMMGKMDFEBGIIIILOJBFCIPANIG'
            }

            print(f"📥 Downloading PDF: {document_url}")
            resp = requests.get(document_url, stream=True, headers=headers)
            resp.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Convert PDF to images
            pages = convert_from_path(filename)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page) + "\n"

            if not text.strip():
                print("⚠️ No text could be extracted from PDF (OCR failed).")
                return

            sample_format = '''
                {
                    "found": true if Property Address Exist else false,
                    "address": Property Address,
                    "zip": Property Address Zip Code,
                    "state": Property Address State,
                    "city": Property Address City,
                    "parcel_number": Parcel No. of the document
                }
            '''
            prompt = f"""
    You are analyzing a foreclosure case document. Extract ONLY the property address. 
    Format it as: street number + street name + city + state + ZIP. 
    If no address is found, respond exactly with the Parcel No. of the Document. 
    Do not include any other information or commentary.

    Here is the document text:
    {text}

    PLEASE FOLLOW THE SAMPLE RESPONSE FORMAT IN JSON:
    {sample_format}

            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise data extractor."},
                    {"role": "user", "content": prompt}
                ]
            )
            data = response.choices[0].message.content.strip()
            # print("🤖 Property Address:", address)
            return data

        except Exception as e:
            print(f"❌ Error while downloading or analyzing PDF: {str(e)}")


if __name__ == "__main__":
    main = Main()
    # main.scrape_via_soup("CV-2025-09-4147")
    main.run()
    # main.scrape_via_workflow2(5604009)