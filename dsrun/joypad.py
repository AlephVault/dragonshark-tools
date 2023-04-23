import threading
import time
import pygame
import subprocess
from .files import settings_get


# The sleep time for each iteration is a half second.
SLEEP_TIME = 0.5
# These are expressed in half-seconds.
HOTKEY_TIME = 3 * 2
GAMEPAD_REFRESH = 10 * 2
# The true default constants.
TRUE_START = 9
TRUE_SELECT = 8
DEFAULT_HOTKEY = (TRUE_START, TRUE_SELECT)
# The setting for the exit hotkey.
EXIT_HOTKEY_SETTING = "exit-hotkey"


def is_hotkey_pressed(gamepad, hotkey=(8, 9)):
    """
    Tells whether the hotkey is pressed. By default, the hotkey
    is START + SELECT.
    """

    pygame.event.pump()
    return all([gamepad.get_button(key) for key in hotkey])


def main_gamepad_and_hotkey():
    """
    Gets the first gamepad, and also the current hotkey.
    """

    joystick = pygame.joystick.Joystick(0)
    if joystick:
        joystick.init()
    settings = settings_get()
    exit_hotkey = settings.get(EXIT_HOTKEY_SETTING)
    if not exit_hotkey or not isinstance(exit_hotkey, (list, tuple)):
        exit_hotkey = DEFAULT_HOTKEY
    return joystick, exit_hotkey


def kill_on_hotkey(process: subprocess.Popen):
    """
    Starts a watch over the process. If the process is not killed and the
    main joypad is pressing Start + Select for 3 seconds, then the process
    will be killed (non-gracefully!).
    :param process: The process to watch.
    """

    def _func():
        refresh_ctr = 0
        gamepad = None
        hotkey = (8, 9)
        hotkey_ctr = 0
        while process.poll() is None:
            if refresh_ctr == GAMEPAD_REFRESH:
                refresh_ctr = 0
            if refresh_ctr == 0:
                gamepad, hotkey = main_gamepad_and_hotkey()
            refresh_ctr += 1

            # Now, work with the main gamepad only. If Start + Select
            # are pressed for 3 seconds or more, then kill the game.
            if gamepad is not None:
                if is_hotkey_pressed(gamepad, hotkey):
                    hotkey_ctr += 1
                    if hotkey_ctr == HOTKEY_TIME:
                        process.kill()
                        return
                else:
                    hotkey_ctr = 0
            time.sleep(SLEEP_TIME)
    threading.Thread(target=_func).start()
