#!/usr/bin/python3
import json
import logging
from dsrun.process import run_game, clear_processes
from dsrun.files import setup_state_files, lock_get, lock_set, command_reader


logging.basicConfig()
LOGGER = logging.getLogger("game-runner")


# This is a service. ALL of this code will be executed in root (!!!) context,
# but the game itself will be always run in "gamer" (gamer:gamer) userspace.
#
# The only user that can issue things to this service is the "pi" (pi:pi).
# This is done through a special fifo (pipe) file, which is ownership-given
# to the pi user (in 0700 mode).


def setup():
    """
    Sets everything up.
    """

    clear_processes()
    setup_state_files()


def teardown():
    """
    Clears everything, just in case the corresponding steps in the process
    cycle did not clear anything.
    """

    clear_processes()


def service():
    """
    The whole service loop.
    """

    with command_reader() as f:
        while True:
            # Get the command.
            try:
                line = f.readline()
                obj = json.loads(line)
                directory = obj["directory"]
                command = obj["command"]
                domain = obj["domain"]
                game_id = obj["game-id"]
            except:
                LOGGER.error("Invalid JSON line: " + line)
                continue

            # Ignore, if there is lock.
            lock_exists, lock_line = lock_get()
            if lock_exists:
                LOGGER.error("A game is already running: " + lock_line)
                continue

            # Otherwise, lock and execute.
            lock_set(line)
            run_game(directory, command, domain, game_id)


def run():
    setup()
    try:
        service()
    finally:
        teardown()


if __name__ == "__main__":
    pass
