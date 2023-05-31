import yaml
from yaml import SafeLoader

class Config():
    def __init__(self):

        with open("config.yaml", "r") as file:
            self.config = yaml.load(file, Loader=SafeLoader)

            # Set the Build version & icon
            self.build_version = "1.2"
            self.webhook_icon = "https://i.imgur.com/aTtaGgp.png"

            # Tool settings
            self.threads = self.config["threads"]
            self.proxy_file = self.config["proxy_file"]
            self.invites_file = self.config["invites_file"]
            self.used_guilds_file = self.config["used_guilds_file"]
            self.output_folder = self.config["output_folder"]
            self.scrape_proxies = self.config["scrape_proxies"]
            self.scraped_proxies_file = self.config["scraped_proxies_file"]

            # Server settings
            self.minimum_members = self.config["minimum_members"]
            self.minimum_online_members = self.config["minimum_online_members"]
            self.maximum_members = self.config["maximum_members"]
            self.minimum_boosts = self.config["minimum_boosts"]
            self.blacklisted_words = self.config["blacklisted_words"]