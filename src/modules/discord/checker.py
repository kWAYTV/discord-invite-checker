import requests, time, os, random
from threading import Lock
from src.modules.utils.logger import Logger
from src.modules.helper.config import Config
from concurrent.futures import ThreadPoolExecutor
from src.modules.helper.proxy_scraper import ProxyScraper

class InviteChecker:

    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.lock = Lock()
        self.proxy_scraper = ProxyScraper()
        self.start_time = time.time()

        # Set the counters to 0
        self.total_invites, self.duped_invites, self.checked_invites, self.valid_invites, self.invalid_invites, self.used_invites_count, self.blacklisted_invites, self.below_min_users_invites, self.below_min_online_invites, self.above_max_users_invites, self.above_min_boosts_invites = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    # Proxy scraper
    def load_proxy_list(self):
        if self.config.scrape_proxies:
            self.proxy_scraper.scrape_proxies()
            proxy_file = self.config.scraped_proxies_file
        else:
            proxy_file = self.config.proxy_file

        with open(proxy_file, "r", encoding="utf8", errors="ignore") as file:
            self.proxy_list = file.read().splitlines()
        return self.proxy_list

    # Set a proxy each request
    def set_proxy(self):
        proxy = random.choice(self.proxy_list)
        return {'http': f"http://{proxy}", 'https': f'http://{proxy}'}

    # Read invites from file
    def load_invites(self):
        with open(self.config.invites_file, "r", encoding="utf8", errors="ignore") as invites_file:
            self.invites = invites_file.read().splitlines()
            self.total_invites = len(self.invites)
            return self.invites

    # Read used invites from file
    def load_used_invites(self):
        with open(self.config.used_guilds_file, "r", encoding="utf8", errors="ignore") as used_invites_file:
            self.used_invites = used_invites_file.read().splitlines()
            return self.used_invites

    # Function to refresh current used invites
    def refresh_current_used(self):
        with open(f"{self.config.output_folder}/used.txt", "r", encoding="utf8", errors="ignore") as current_used_invites_file:
            self.current_used_invites = current_used_invites_file.read().splitlines()
            return self.current_used_invites

    # Function to get Checks Per Minute
    def get_cpm(self):
        elapsed_time = time.time() - self.start_time
        elapsed_minutes = elapsed_time / 60
        cpm = self.checked_invites / elapsed_minutes
        cpm = round(cpm, 0)
        return cpm

    # Process invite with ThreadPoolExecutor
    def process_invite(self, invite):
        session = requests.Session()
        session.proxies = self.set_proxy()
        self.refresh_current_used()

        invite_code = invite.replace("https://", "").replace("discord.gg/", "").replace("discord.com/invite/", "")

        response = session.get(f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true")

        with self.lock:
            self.checked_invites += 1

            self.logger.change_title(f"Discord Invite Checker {self.config.build_version} • CPM: {self.get_cpm()} • Checked: {self.checked_invites}/{self.total_invites} • Valid: {self.valid_invites} • Invalid: {self.invalid_invites} • Blacklisted: {self.blacklisted_invites} • Used: {self.used_invites_count} • Below Min Users: {self.below_min_users_invites} • Below Min Online: {self.below_min_online_invites} • Above Max Users: {self.above_max_users_invites} • Above Min Boosts: {self.above_min_boosts_invites} • discord.gg/kws")

            # Check if the invite is valid
            if response.status_code == 404:
                self.invalid_invites += 1
                with open(f"{self.config.output_folder}/invalid.txt", "a", encoding="utf8", errors="ignore") as invalid_invites_file:
                    invalid_invites_file.write(f"{invite}\n")
                return

            # Get the response as json
            json_data = response.json()

            guild_name = json_data["guild"]["name"]
            guild_id = json_data["guild"]["id"]
            guild_boosts = json_data["guild"]["premium_subscription_count"]
            guild_members = json_data["approximate_member_count"]
            guild_online_members = json_data["approximate_presence_count"]

            # Check if the invite is already used
            if guild_id in self.used_invites:
                self.used_invites_count += 1
                with open(f"{self.config.output_folder}/used.txt", "a", encoding="utf8", errors="ignore") as used_invites_file:
                    used_invites_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Invite already used: {guild_name} ({guild_id})")
                return
            
            # Check if the invite is already in current used
            if guild_id in self.current_used_invites:
                self.used_invites_count += 1
                with open(f"{self.config.output_folder}/used.txt", "a", encoding="utf8", errors="ignore") as used_invites_file:
                    used_invites_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Invite already used: {guild_name} ({guild_id})")
                return

            # Check if the guild name contains a blacklisted word
            for word in self.config.blacklisted_words:
                if word.lower() in guild_name.lower():
                    self.blacklisted_invites += 1
                    with open(f"{self.config.output_folder}/blacklisted.txt", "a", encoding="utf8", errors="ignore") as blacklisted_invites_file:
                        blacklisted_invites_file.write(f"{invite}\n")
                    self.logger.log("BAD", f"Blacklisted word found in guild name: {guild_name} ({guild_id})")
                    return

            # Check if the guild has enough members
            if guild_members < self.config.minimum_members:
                self.below_min_users_invites += 1
                with open(f"{self.config.output_folder}/below_min_users.txt", "a", encoding="utf8", errors="ignore") as below_min_users_file:
                    below_min_users_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Guild has less than {self.config.minimum_members} members: {guild_name} ({guild_id})")
                return

            # Check if the guild has enough online members
            if guild_online_members < self.config.minimum_online_members:
                self.below_min_online_invites += 1
                with open(f"{self.config.output_folder}/below_min_online.txt", "a", encoding="utf8", errors="ignore") as below_min_online_file:
                    below_min_online_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Guild has less than {self.config.minimum_online_members} online members: {guild_name} ({guild_id})")
                return

            # Check if the guild has too many members
            if guild_members > self.config.maximum_members:
                self.above_max_users_invites += 1
                with open(f"{self.config.output_folder}/above_max_users.txt", "a", encoding="utf8", errors="ignore") as above_max_users_file:
                    above_max_users_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Guild has more than {self.config.maximum_members} members: {guild_name} ({guild_id})")
                return

            # Check if the guild has enough boosts
            if guild_boosts < self.config.minimum_boosts:
                self.above_min_boosts_invites += 1
                with open(f"{self.config.output_folder}/above_min_boosts.txt", "a", encoding="utf8", errors="ignore") as above_min_boosts_file:
                    above_min_boosts_file.write(f"{invite}\n")
                self.logger.log("BAD", f"Guild has less than {self.config.minimum_boosts} boosts: {guild_name} ({guild_id})")
                return

            # If the guild is valid, write it to the output file
            self.valid_invites += 1
            with open(f"{self.config.output_folder}/valid.txt", "a", encoding="utf8", errors="ignore") as valid_invites_file:
                valid_invites_file.write(f"{invite}\n")
            with open(f"{self.config.output_folder}/used.txt", "a", encoding="utf8", errors="ignore") as used_invites_file:
                used_invites_file.write(f"{guild_id}\n")
            self.logger.log("OK", f"Valid guild found: {guild_name} ({guild_id})")

    # Start the checker
    def start(self):    

        # Load invites from file
        self.logger.log("INFO", "Loading invites...")
        self.load_invites()

        # Load used invites from file
        self.logger.log("INFO", "Loading used invites...")
        self.load_used_invites()

        # Load proxies from file
        self.logger.log("INFO", "Loading proxies...")
        self.load_proxy_list()

        # Start ThreadPoolExecutor  
        self.logger.log("INFO", "Starting threads...")

        if self.total_invites > self.config.threads:
            threads = self.total_invites
        else:
            threads = self.config.threads

        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.process_invite, self.invites)
        
        self.shutdown()

    # Function to shut everything off and log the stats when it's done
    def shutdown(self):
        print("")
        self.logger.log("SUCCESS", "Done! Shutting down...")
        self.logger.log("INFO", f"Checked: {self.checked_invites}/{self.total_invites} • Valid: {self.valid_invites} • Invalid: {self.invalid_invites} • Blacklisted: {self.blacklisted_invites} • Used: {self.used_invites_count} • Below Min Users: {self.below_min_users_invites} • Below Min Online: {self.below_min_online_invites} • Above Max Users: {self.above_max_users_invites} • Above Min Boosts: {self.above_min_boosts_invites}")
        self.logger.log("INFO", "Goodbye!")
        exit()

if __name__ == "__main__":
    checker = InviteChecker()
    checker.start()