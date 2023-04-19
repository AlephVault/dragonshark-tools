import os
import re
import logging
import subprocess
from typing import Callable
from . import exe_game, web_game
from .users import GAMER_NAME
from .files import lock_delete


logging.basicConfig()
LOGGER = logging.getLogger("game-runner")


def clear_processes():
    """
    Clears all the gamer:gamer processes properly. Fuck everything: the
    children processes, if any, will be hard-killed. This also destroys
    whatever dangling crontab processes the user set up. No crontab is
    allowed for this user.
    """

    os.system(f"crontab -u {GAMER_NAME} -r")
    os.system(f"pkill -9 -u {GAMER_NAME}")
    lock_delete()


def get_executable_type(path: str):
    """
    Tells whether the executable is an HTML page (returns "web") or another type.
    This "another type" might be an ELF 32-bit or ELF 64-bit, or a shell script,
    but in any case the command type will be the same for them (returns "exe").
    :returns: The type: "web" or "exe".
    """

    if not os.path.isfile(path):
        raise Exception(f"Command not found: {path}")
    output = subprocess.check_output(["file", path]).decode('utf-8')
    if re.search(r"HTML document", output):
        return "web"
    else:
        return "exe"


def validate_command(directory: str, command: str, on_end: Callable[[], None]):
    """
    Validates the command being included in the directory (part of it).
    :param directory: The game directory.
    :param command: The command.
    :param on_end: What to do on invalid command.
    :return: None if the command is not inside the directory. Otherwise, the fixed command.
    """

    full_command = os.path.join(directory, command)
    prefix = directory.rstrip("/") + "/"
    if not full_command.startswith(prefix):
        LOGGER.error(f"The command '{command}' is not inside the directory '{directory}'")
        on_end()
        return None
    return full_command[len(prefix):]


def run_game(directory: str, command: str, domain: str, app: str):
    """
    Executes a game. For non-web games, a save-file mechanism will be attempted.
    :param directory: Where is the game stored.
    :param command: The command, inside the game.
    :param domain: The domain of the game. This is INVERTED, typically in the
      same format for Java or React. Something like "com.mycompany".
    :param app: The name of the game. It might be something like this:
      "MyAwesomeGame" or "MyAwesomeGame.Main" (perhaps the game has multiple
      possible interfaces).
    """

    # 1. Determine the command to exist, actually. And determine it being
    #    a web game or not.
    process_type = get_executable_type(os.path.join(directory, command))

    # 2. Determine the command type and methods to use.
    if process_type == "web":
        callback = lock_delete
        runner = web_game.run_game
    else:
        callback = clear_processes
        runner = exe_game.run_game

    # 3. Run the command.
    real_command = validate_command(directory, command, callback)
    if real_command:
        runner(directory, real_command, domain, app, callback)
