import os, logging, sys
from src.modules.utils.logger import Logger
from src.modules.helper.config import Config
from src.modules.helper.filemanager import FileManager
from src.modules.discord.checker import InviteChecker

#Don't create .pyc
sys.dont_write_bytecode = True

# Set title
if os.name == 'nt':
    os.system(f"title Discord Invite Checker • Starting... • discord.gg/kws")

# Set logging system
logging.basicConfig(handlers=[logging.FileHandler('invite_checker.log', 'w+', 'utf-8')], level=logging.ERROR, format='%(asctime)s: %(message)s')

# Main class
class Main():
    def __init__(self) -> None:
        self.config = Config()
        self.logger = Logger()
        self.filemanager = FileManager()
        self.invite_checker = InviteChecker()

    def start(self):
        # Prepare the console
        self.logger.print_logo()

        # Check if the input files are valid
        self.filemanager.check_input()

        # Start checking invites
        self.invite_checker.start()

if __name__ == "__main__":
    try:
        Tool = Main()
        Tool.start()
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        logging.error(f"ERROR: {e}")