import os
import subprocess
import threading
from typing import Callable
from .users import PI_NAME, GAMER_NAME

# This is the partition where all the Dragonshark saves exist.
# This partition is ext4 and everything there will be owned by pi.
# Actually, the partition is /mnt/SAVES, with the usual "rwxr-xr-x"
# permissions, and owned by pi:pi (recursively). Additionally, the
# "dragonshark" subdirectory will keep saves for all of the games
# (/mnt/SAVES/{domain}/{game} for each game).
SAVES_LOCATION = "/mnt/SAVES/dragonshark"

# This is another partition. This one is mounted as vfat instead,
# thus becoming totally permission-less. This is because, here,
# the user which will run the game is not "pi"pi", as in web games,
# but instead it will be "gamer:gamer" (to protect "pi:pi" from any
# potentially unknown malicious apps disguised as a game from doing
# any harm to the user's data), since "gamer:gamer" is homeless and
# has no permissions at all anywhere.
CURRENT_SAVE_LOCATION = "/mnt/CURRENT_SAVE"


def run_game(directory: str, command: str, domain: str, app: str, on_end: Callable[[], None]):
    """
    Executes a native game.
    :param directory: Where is the game stored.
    :param command: The command, inside the game.
    :param domain: The domain of the game. This is INVERTED, typically in the
      same format for Java or React. Something like "com.mycompany".
    :param app: The name of the game. It might be something like this:
      "MyAwesomeGame" or "MyAwesomeGame.Main" (perhaps the game has multiple
      possible interfaces).
    :param on_end: What happens when the game is completely terminated and
      cleaned up.
    """

    # The steps for this one are the following:
    # 1. Clear the current save partition.
    os.system(f"rm -rf {CURRENT_SAVE_LOCATION}/*")
    # 2. Copy the contents from the saves partition (for the game, only)
    #    to the current save partition. Make the game save directory if
    #    it does not exist beforehand.
    game_dir = os.path.join(SAVES_LOCATION, domain, app)
    os.system(f"sudo -u {PI_NAME} mkdir -p {game_dir}")
    os.system(f"cp {game_dir}/* {CURRENT_SAVE_LOCATION}")
    # 3. Run the game.
    process = subprocess.Popen(["sudo", "-u", GAMER_NAME, os.path.join(directory, command)])

    # When the game process ends:
    def _func():
        process.wait()
        # 4. Copy the contents from the current save partition to the saves
        #    partition (chown to pi:pi, with 0o400).
        os.system(f"rm -r {game_dir}/*")
        os.system(f"cp {CURRENT_SAVE_LOCATION}/* {game_dir}")
        # 5. Clear, again, the current save partition.
        os.system(f"rm -rf {CURRENT_SAVE_LOCATION}/*")
        # 6. Invoke the on_end callback properly.
        on_end()
    threading.Thread(target=_func).start()
