import requests
from src.modules.utils.logger import Logger
from src.modules.helper.config import Config

class ProxyScraper():

    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.session = requests.Session()

    # Function to scrape proxies
    def scrape_proxies(self):
        self.logger.log("INFO", "Scraping proxies...")

        response = self.session.get("https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all")

        if response.status_code != 200:
            self.logger.log("ERROR", "Failed to scrape proxies, please try again later or use your own.")
            return
        
        proxy_list = response.text.splitlines()
        
        with open(self.config.scraped_proxies_file, "w+") as f:
            f.write('\n'.join(proxy_list) + '\n')

        self.logger.log("SUCCESS", f"Successfully scraped {len(response.text.splitlines())} proxies.")

        return response.text.splitlines()
