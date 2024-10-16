from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import traceback

def web_scrapper(url):
    print(f"Starting web_scrapper for URL: {url}", file=sys.stderr)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    service = Service("/usr/local/bin/chromedriver")

    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            print("WebDriver initialized successfully", file=sys.stderr)
            driver.get(url)
            print("URL loaded successfully", file=sys.stderr)

            page_source = driver.page_source
            print(f"Page source retrieved. Length: {len(page_source)}", file=sys.stderr)

        # Process the page source outside the webdriver context
        soup = BeautifulSoup(page_source, 'html.parser')
        print("Page source parsed with BeautifulSoup", file=sys.stderr)

        company_description = soup.find('meta', attrs={'name': 'description'})
        company_description = company_description['content'] if company_description else 'Meta description not found.'

        company_info = [element.get_text(strip=True) for element in soup.find_all(['h1', 'h2', 'h3', 'p']) if element.get_text(strip=True)]

        about_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) 
                       if 'about' in a.get_text(strip=True).lower() or 'about' in a['href'].lower()]

        print(f"Found {len(company_info)} info items and {len(about_links)} about links", file=sys.stderr)

        return {
            'description': company_description,
            'info': company_info[:5],  # Limit to first 5 items
            'about_links': about_links[:3]  # Limit to first 3 about links
        }

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None
