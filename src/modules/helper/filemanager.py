import os
from src.modules.utils.logger import Logger
from src.modules.helper.config import Config

defaultConfig = """
# Discord Invite Checker - discord.gg/kws

# Tool settings
threads: 250 # Threads to use
proxy_file: "/src/data/input/proxies.txt" # Proxy file to use
invites_file: "/src/data/input/invites.txt" # Invites file to use
used_guilds_file: "/src/data/input/used.txt" # Used guilds file to use
output_folder: "/src/data/output" # Output folder to use
scrape_proxies: true # Scrape proxies or not
scraped_proxies_file: "src/data/output/scraped_proxies.txt" # Scraped proxies file to use

# Server settings
minimum_members: 300 # Minimum members to check for
minimum_online_members: 100 # Minimum online members to check for
maximum_members: 75000 # Maximum members to check for
minimum_boosts: 1 # Minimum boosts to check for
blacklisted_words: # Blacklisted words to check for
  - giveaway
  - nitro
  - free
  - join
  - invite
"""

class FileManager():

    def __init__(self):
        self.logger = Logger()
        self.config = Config()

    # Function to check if the input files are valid
    def check_input(self):

        # if there is no config file, create one.
        if not os.path.isfile("config.yaml"):
            self.logger.log("INFO", "Config file not found, creating one...")
            open("config.yaml", "w+").write(defaultConfig)
            self.logger.log("INFO", "Successfully created config.yml, please fill it out and try again.")
            exit()

        # if there is no emails in /src/data/input/emails.txt, exit the tool.
        if os.stat(self.config.proxy_file).st_size == 0:
            self.logger.log("ERROR", "There is no proxies in /src/data/input/proxies.txt, please add some proxies and try again.")
            exit()

        # if there is no emails in /src/data/input/proxies.txt, exit the tool.
        if os.stat(self.config.invites_file).st_size == 0:
            self.logger.log("ERROR", "There is no invites in /src/data/input/invites.txt, please add some invites and try again.")
            exit()

        # check if any invite code is duplicated and leave only one
        with open(self.config.invites_file, "r") as f:
            seen_codes = set()
            seen_links = []
            lines = f.read().splitlines()
            for line in lines:
                invite_code = line.replace("https://", "").replace("discord.gg/", "").replace("discord.com/invite/", "")
                if invite_code not in seen_codes:
                    seen_codes.add(invite_code)
                    seen_links.append(line)
            self.logger.log("INFO", "Removed {} duplicated invite codes.".format(len(lines) - len(seen_links)))

        with open(self.config.invites_file, "w") as f:
            f.write("\n".join(seen_links))
