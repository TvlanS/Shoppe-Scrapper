from botasaurus_humancursor import WebCursor
from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
import time
import threading
#import keyboard

from utils.Shop_tools import ProductScraper

profile_name = "Sapota"
tiny = False

def wait_for_captcha_resolution(driver: Driver, timeout: int = 120):
    """
    Detects if a CAPTCHA is present and waits for the user to solve it.
    Returns True if CAPTCHA was detected and resolved, False if no CAPTCHA found.
    """
    try:
        # Check for the CAPTCHA element using its ID or aria-label
        captcha_present = driver.find_elements_by_css_selector(
            "#NEW_CAPTCHA, [aria-label*='Solve the CAPTCHA'], [aria-label*='verify you are not a bot']"
        )
        
        if not captcha_present:
            return False
            
        print("⚠️  CAPTCHA detected! Please solve it in the browser window...")
        print(f"   Waiting up to {timeout} seconds for you to complete verification...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if CAPTCHA has disappeared (user solved it)
            captcha_still_present = driver.find_elements_by_css_selector(
                "#NEW_CAPTCHA, [aria-label*='Solve the CAPTCHA'], [aria-label*='verify you are not a bot']"
            )
            
            if not captcha_still_present:
                print("✅ CAPTCHA resolved! Continuing...")
                time.sleep(1)  # Brief pause after resolution
                return True
                
            time.sleep(1)  # Poll every second
        
        print("⏰ CAPTCHA timeout reached. Skipping and continuing...")
        return False
        
    except Exception as e:
        print(f"CAPTCHA check error: {e}")
        return False

@browser(output=None,tiny_profile= tiny, profile = profile_name)
def scrape_main_card(driver: Driver, url: str):
    driver.enable_human_mode()

    driver.google_get(url, bypass_cloudflare=True)
    wait_for_captcha_resolution(driver, 120)
    driver.wait_for_element(".shopee-search-item-result__item", wait=8)


    try:
        
        #cursor = WebCursor(driver)
        #cursor.click([158, 286])

        time.sleep(5)

        print("Scrolling to bottom of the page...")
        driver.scroll_to_bottom()

        

    except Exception as e:
        print(f"Error occurred: {e}")
        driver.disable_human_mode()

    driver.wait_for_element(".shopee-search-item-result__item", wait=8)

    soup = soupify(driver)
    items = soup.select(".shopee-search-item-result__item")

    product_scraper = ProductScraper(items)
    data = product_scraper.scrapping_contents()

    return data  # also removed the curly braces, {data} creates a set not a dict

# open
# if no product skip
# if inva;id page put link on hold
# create a new folder

@browser(output=None, tiny_profile= tiny, profile = profile_name)
def scrape_sub_cards(driver: Driver, url: str):
    driver.google_get(url, bypass_cloudflare=True)
    #wait_for_captcha_resolution(driver, 120)
    # Wait for either one of the 3 possible states
    driver.wait_for_element(
        ".BsK01h, .shopee-search-empty-result-section__title, .shopee-search-item-result__item",
        wait=8
    )

    soup = soupify(driver)

    # Check which state we're in
    if soup.select_one(".BsK01h"):
        print("Page Unavailable")
        return "Page Unavailable"

    elif soup.select_one(".shopee-search-empty-result-section__title"):
        print("No products found in this shop")
        return "No Products"

    else:
        #items = soup.select(".shopee-search-item-result__item")
        #product_scraper = ProductScraper(items)
        #data = product_scraper.scrapping_contents()
        print("Products Available")
        return "Products Available"

@browser(output=None, tiny_profile= tiny, profile = profile_name)
def login(driver: Driver, url: str):

    driver.enable_human_mode()

    driver.google_get(url, bypass_cloudflare=True)

    time.sleep(50)

    driver.disable_human_mode()

    return print("Login Mode Closed")


class ScrapeShopee:
    def __init__(self, url: str):
        self.url = url

    def run_main(self):
        return scrape_main_card(self.url)
    
    def run_sub(self):
        return scrape_sub_cards(self.url)
    
    def run_login(self):
        return login(self.url)


