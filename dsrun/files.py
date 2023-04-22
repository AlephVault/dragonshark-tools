import os
import json
import logging
from .users import PI_UID, PI_GID


# Two files will be defined in this context. One is the lock to tell which game
# is being run (a full command is stored) and the other one is the pipe that
# sends/receives the game execution commands.
GAME_LOCK_FILE = "/run/game/lock"
PIPE_FILE = "/run/game/command-awaiter"
# Also, a file holding several settings will be held here.
SETTINGS_FILE = "/etc/dragonshark/settings.json"


logging.basicConfig()
LOGGER = logging.getLogger("game-runner")


def clear_state_files():
    """
    Clears the two related state files: lock and pipe.
    """

    try:
        # Remove the FIFO, if existing.
        os.unlink(PIPE_FILE)
    except:
        # Yes: a diaper.
        pass

    try:
        # Remove the LOCK, if existing.
        os.unlink(GAME_LOCK_FILE)
    except:
        # Yes: a diaper.
        pass


def setup_state_files():
    """
    Prepares the fifo that is granted to the given user.
    """

    # Clears the state files.
    clear_state_files()
    # Creates the files directory.
    os.system("mkdir -p /run/game")
    # [re-]Creates the pipe file.
    os.mkfifo(PIPE_FILE)
    # The given user will only have, by default, write-only permission.
    # The root user will always have permission to read, because... root.
    os.chmod(PIPE_FILE, 0x200)
    os.chown(PIPE_FILE, PI_UID, PI_GID)


def lock_get():
    """
    Gets the contents of the current lock.
    :return: A pair (exists, content) for the lock.
    """

    if os.path.isfile(GAME_LOCK_FILE):
        with open(GAME_LOCK_FILE, 'r') as lf:
            return True, lf.readline()
    else:
        return False, ""


def lock_set(line):
    """
    Sets the contents of the current lock.
    :param line: The line to store.
    """

    with open(GAME_LOCK_FILE, 'w') as f:
        f.write(line.strip('\n') + '\n')


def lock_delete():
    """
    Deletes the lock.
    """

    os.remove(GAME_LOCK_FILE)


def command_reader():
    """
    Returns a handle to the existing pipe.
    :return: The handle.
    """

    return open(PIPE_FILE, 'r')


def settings_get():
    """
    Returns a handle to the hotkeys file.
    :return: The handle.
    """

    try:
        with open(SETTINGS_FILE, 'r') as f:
            result = json.load(f)
            if isinstance(result, dict):
                return result
            else:
                LOGGER.error("The settings is not a valid dictionary. Returning default settings")
                return {}
    except OSError:
        LOGGER.error(f"Could not open {SETTINGS_FILE}. Returning default settings")
        return {}
    except Exception as e:
        LOGGER.exception("An error occurred. Returning default settings")
        return {}


def settings_set(settings):
    """
    Updates the settings.
    :param settings:
    :return:
    """

    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)
