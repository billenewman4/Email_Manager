from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def web_scrapper(url):
    # Initialize the Selenium WebDriver
    driver = webdriver.Chrome()

    try:
        # Use Selenium to load the page
        driver.get(url)

        # Get the page source after the JavaScript has been executed
        page_source = driver.page_source

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Initialize variables
        company_description = ''
        company_info = []
        about_links = []

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            company_description = meta_desc['content']
        else:
            company_description = 'Meta description not found.'

        # Extract text from headings and paragraphs
        elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        if elements:
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    company_info.append(text)
        else:
            company_info.append('No headings or paragraphs found.')

        # Find 'About Us' links
        links = soup.find_all('a', href=True)
        if links:
            for a in links:
                href = a['href']
                text = a.get_text(strip=True).lower()
                href_lower = href.lower()
                if 'about' in text or 'about' in href_lower:
                    full_url = urljoin(url, href)
                    about_links.append(full_url)
        else:
            about_links.append('No links found.')

        if not about_links:
            about_links.append('No "About Us" links found.')

        # Output the results
        print('Company Description:')
        print(company_description)
        print('\nCompany Info:')
        for info in company_info:
            print(info)
        print('\nAbout Us Links:')
        for link in about_links:
            print(link)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()