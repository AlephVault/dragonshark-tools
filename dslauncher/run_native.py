import os
import subprocess
import threading
from typing import Callable
from .hotkeys import kill_on_hotkey
from .saves import load_dragonshark_save, store_dragonshark_save


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
    load_dragonshark_save(package, app)

    # 2. Run the game.
    process = subprocess.Popen(["sudo", "-u", "gamer", os.path.join(directory, command)])

    def _func():
        process.wait()
        # Clear cron entries, at entries, and any remaining process.
        os.system(f"crontab -u gamer -r")
        os.system(f"atrm -u gamer")
        os.system(f"pkill -9 -u gamer")
        # Save whatever game state remains.
        store_dragonshark_save(package, app)
        on_end()
    threading.Thread(target=_func).start()

    # 3. Wait until the game process ends:
    # Also install a signal to kill it on hotkey Start + Select (hold both 3 seconds).
    kill_on_hotkey(process)
