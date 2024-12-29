from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import time
from bs4 import BeautifulSoup
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class SeleniumScraper:
    def __init__(self):
        self.setup_chrome_options()
        self.driver_path = self.get_driver_path()
        self.setup_keywords()

    def setup_chrome_options(self):
        """Set up Chrome options for the WebDriver."""
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    def setup_keywords(self):
        """Set up keyword dictionaries for different categories."""
        self.keywords = {
            'Probiotics': [
                'probiotic', 'probiotics', 'beneficial bacteria', 'live cultures', 
                'gut flora', 'microbiome', 'lactobacillus', 'bifidobacterium'
            ],
            'Fortification': [
                'fortified', 'fortification', 'enriched', 'vitamins', 'minerals',
                'nutrient enrichment', 'added nutrients', 'supplemented'
            ],
            'Gut Health': [
                'digestive health', 'gut health', 'digestive wellness', 'microbiome',
                'digestive system', 'gut barrier', 'intestinal health'
            ],
            "Women's Health": [
                'women\'s health', 'feminine', 'pregnancy', 'menopause',
                'women wellness', 'maternal health', 'female health'
            ],
            'Cognitive Health': [
                'brain health', 'cognitive', 'memory', 'mental clarity',
                'brain function', 'mental performance', 'cognitive function'
            ],
            'Sports Nutrition': [
                'sports nutrition', 'athletic', 'performance', 'protein powder',
                'exercise recovery', 'sports performance', 'muscle recovery'
            ]
        }

        self.category_keywords = {
            'Manufacturer': [
                'manufacturer', 'manufacturing', 'production', 'facility', 
                'factory', 'plants', 'produces', 'manufacturing facility'
            ],
            'Brand': [
                'brand', 'products', 'our range', 'portfolio', 
                'our brands', 'product line', 'offerings'
            ],
            'Distributor': [
                'distributor', 'distribution', 'wholesale', 'supply chain',
                'logistics', 'suppliers', 'dealer network'
            ]
        }

    def get_driver_path(self):
        """Get the path to chromedriver."""
        driver_path = Path('drivers') / 'chromedriver.exe'
        
        if not driver_path.exists():
            raise FileNotFoundError(
                "\nChromeDriver not found! Please follow these steps:\n"
                "1. Create a 'drivers' folder in your project directory\n"
                "2. Download ChromeDriver from https://sites.google.com/chromium.org/driver/\n"
                "3. Extract chromedriver.exe to the 'drivers' folder\n"
                "4. Ensure ChromeDriver version matches your Chrome browser version"
            )
        
        return str(driver_path)

    def create_driver(self):
        """Create and return a new WebDriver instance."""
        try:
            service = Service(self.driver_path)
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            logging.error(f"Error creating WebDriver: {str(e)}")
            raise

    def search_keywords(self, text, category):
        """Search for category-specific keywords in text."""
        if category in self.keywords:
            return any(keyword.lower() in text.lower() for keyword in self.keywords[category])
        elif category in self.category_keywords:
            return any(keyword.lower() in text.lower() for keyword in self.category_keywords[category])
        return False

    def scroll_page(self, driver):
        """Scroll the page to load dynamic content."""
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # Limit scrolling to 3 attempts
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
        except Exception as e:
            logging.warning(f"Error while scrolling: {str(e)}")

    def scrape_website(self, url):
        """Scrape website using Selenium WebDriver."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        driver = None
        try:
            logging.info(f"Attempting to scrape {url}")
            driver = self.create_driver()
            driver.get(url)
            
            # Wait for the body to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to load any lazy-loaded content
            self.scroll_page(driver)
            
            # Get page content
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Get all text content from meaningful tags
            text_content = ' '.join([
                tag.get_text() 
                for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div'])
            ]).lower()
            
            results = {
                'Website': url,
                'Category': 'F&B' if any(word in text_content for word in ['food', 'beverage', 'nutrition', 'drink', 'snack', 'dairy']) else 'Bulk'
            }
            
            # Check main categories
            for category in ['Manufacturer', 'Brand', 'Distributor']:
                results[category] = 'Yes' if self.search_keywords(text_content, category) else 'No'
            
            # Check specific categories
            for category in self.keywords.keys():
                results[category] = 'Yes' if self.search_keywords(text_content, category) else 'No'
            
            # Determine relevance based on any health/nutrition category being 'Yes'
            health_categories = [
                'Probiotics', 'Fortification', 'Gut Health', 
                "Women's Health", 'Cognitive Health', 'Sports Nutrition'
            ]
            
            results['Relevant'] = 'Yes' if any(results[category] == 'Yes' for category in health_categories) else 'No'
                
            return results
            
        except TimeoutException:
            logging.error(f"Timeout while scraping {url}")
            return self.create_error_result(url)
        except WebDriverException as e:
            logging.error(f"WebDriver error for {url}: {str(e)}")
            return self.create_error_result(url)
        except Exception as e:
            logging.error(f"Unexpected error scraping {url}: {str(e)}")
            return self.create_error_result(url)
        finally:
            if driver:
                driver.quit()

    def create_error_result(self, url):
        """Create an error result dictionary."""
        return {
            'Website': url,
            'Relevant': 'Error',
            'Category': 'Error',
            'Manufacturer': 'Error',
            'Brand': 'Error',
            'Distributor': 'Error',
            'Probiotics': 'Error',
            'Fortification': 'Error',
            'Gut Health': 'Error',
            "Women's Health": 'Error',
            'Cognitive Health': 'Error',
            'Sports Nutrition': 'Error'
        }

    def scrape_multiple_websites(self, urls):
        """Scrape multiple websites and return results as DataFrame."""
        results = []
        for url in urls:
            result = self.scrape_website(url)
            if result:
                results.append(result)
            time.sleep(3)  # Delay between requests
            
        df = pd.DataFrame(results)
        if not df.empty:
            logging.info("\nScraping Results:")
            print(df)  # Print full DataFrame
            return df
        else:
            logging.warning("\nNo results were obtained.")
            return pd.DataFrame()

def main():
    # Create drivers directory if it doesn't exist
    os.makedirs('drivers', exist_ok=True)
    
    websites = [
        "www.nestle.com",
        "www.drreddys.com",
        "colacompany.com",
        "www.pfizer.com",
        "www.pepsico.com",
        "www.jnj.com",
        "www.danone.com",
        "www.bayer.com",
        "www.generalmills.com",
        "www.gsk.com",
        "www.kelloggs.com",
        "www.merck.com",
        "www.unilever.com",
        "www.roche.com",
        "www.nestlewaters.com",
        "www.sanofi.com",
        "www.mondelezinternational.com",
        "www.novartis.com",
        "www.kraftheinzcompany.com",
        "www.lilly.com",
        "www.tysonfoods.com",
        "www.tevapharm.com",
        "www.mars.com",
        "www.abbvie.com",
        "www.campbellsoupcompany.com",
        "www.amgen.com",
        "www.conagrabrands.com",
        "www.astrazeneca.com",
        "www.molsoncoors.com",
        "www.boehringeringelheim.com",
        "www.abinbev.com",
        "www.basf.com",
        "www.diageo.com",
        "www.pg.com",
        "www.theheinekencompany.com",
        "www.medtronic.com",
        "www.mckesson.com",
        "www.amerisourcebergen.com",
        "www.cardinalhealth.com",
        "www.medline.com"
    ]
    
    try:
        scraper = SeleniumScraper()
        results_df = scraper.scrape_multiple_websites(websites)
        
        if not results_df.empty:
            results_df.to_csv('website_analysis.csv', index=False)
            logging.info("\nResults saved to 'website_analysis.csv'")
            
    except FileNotFoundError as e:
        logging.error(f"\nSetup Error: {str(e)}")
    except Exception as e:
        logging.error(f"\nUnexpected Error: {str(e)}")

if __name__ == "__main__":
    main()