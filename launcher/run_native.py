import os
import logging
import subprocess
import threading
from typing import Callable
from .hotkeys import do_on_hotkey
from .saves import load_dragonshark_save, store_dragonshark_save


LOGGER = logging.getLogger("launch-server:run-native")
LOGGER.setLevel(logging.INFO)


def run_game(directory: str, command: str, package: str, app: str, on_end: Callable[[], None]):
    """
    Executes a native game.
    :param directory: Where is the game stored.
    :param command: The command, inside the game.
    :param package: The game's package.
    :param app: The game's app.
    :param on_end: What happens when the game is completely terminated and cleaned up.
    """

    # The steps for this one are the following:
    # 1. Load the current game's saves.
    LOGGER.info("Preparing save directory")
    load_dragonshark_save(package, app)

    # 2. Run the game.
    LOGGER.info("Running the game")
    process = subprocess.Popen(["sudo", "-u", "gamer", os.path.join(directory, command)])

    def _func():
        process.wait()
        # Clear cron entries, at entries, and any remaining process.
        LOGGER.info("Clearing any potential crontab/atrm entry, and killing dangling processes")
        os.system(f"crontab -u gamer -r")
        os.system(f"atrm -u gamer")
        os.system(f"pkill -9 -u gamer")
        # Save whatever game state remains.
        LOGGER.info("Storing save directory")
        store_dragonshark_save(package, app)
        on_end()
    threading.Thread(target=_func).start()

    # 3. Wait until the game process ends:
    # Also install a signal to kill it on hotkey Start + Select (hold both 3 seconds).
    def check():
        return process.poll() is None

    def terminate():
        process.kill()

    do_on_hotkey(check, terminate)
