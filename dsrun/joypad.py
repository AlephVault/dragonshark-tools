import threading
import time
import evdev
import subprocess


# The sleep time for each iteration is a half second.
SLEEP_TIME = 0.5
# These are expressed in half-seconds.
HOTKEY_TIME = 3 * 2
GAMEPAD_REFRESH = 10 * 2


def kill_on_hotkey(process: subprocess.Popen):
    """
    Starts a watch over the process. If the process is not killed and the
    main joypad is pressing Start + Select for 3 seconds, then the process
    will be killed (non-gracefully!).
    :param process: The process to watch.
    """

    def _func():
        refresh_ctr = 0
        main_gamepad = None
        hotkey_ctr = 0
        while process.poll() is None:
            if refresh_ctr == GAMEPAD_REFRESH:
                refresh_ctr = 0
            if refresh_ctr == 0:
                # Determine which one is the [new] main gamepad.
                main_gamepad = None
                for device in evdev.list_devices():
                    try:
                        main_gamepad = evdev.InputDevice(device)
                        break
                    except Exception:
                        pass
            refresh_ctr += 1

            # Now, work with the main gamepad only. If Start + Select
            # are pressed for 3 seconds or more, then kill the game.
            if main_gamepad is not None:
                hotkey = True
                event = main_gamepad.read_one()
                # TODO continue tomorrow. The event must be present (not
                # TODO that much in the past) and must have Select and
                # TODO Start both pressed. Otherwise, hotkey becomes False.
                if hotkey:
                    hotkey_ctr += 1
                    if hotkey == HOTKEY_TIME:
                        process.kill()
                        return
                else:
                    hotkey_ctr = 0
            time.sleep(SLEEP_TIME)
    threading.Thread(target=_func).start()
