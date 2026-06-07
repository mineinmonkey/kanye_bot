import json
import logging
import socket
import time

import constants

logger = logging.getLogger(__name__)


def wait_for_internet(host="8.8.8.8", port=53, timeout=1):
    socket.setdefaulttimeout(timeout)
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                logger.info("Connected to internet!")
                break
        except Exception:
            logger.info("Waiting for internet connection...")
            time.sleep(5)


def init_counter_json() -> None:
    initial_json = {"total": 0, "users": {}}
    save_json(initial_json, constants.COUNTER_JSON_PATH)


def init_gif_json() -> None:
    initial_json = {
        "gifs": {"good": [], "bad": [], "lgood": [], "lbad": []},
        "weights": [],
    }
    save_json(initial_json, constants.GIF_JSON_PATH)


def init_react_json() -> None:
    initial_json = {}
    save_json(initial_json, constants.REACT_JSON_PATH)


def load_json(file_path: str) -> dict:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Couldn't load JSON file, returning empty dictionary")
        return dict()


def save_json(json_dict: dict, file_path: str, indent=None) -> None:
    try:
        with open(file_path, "w") as f:
            json.dump(json_dict, f, indent=indent)
    except Exception:
        logger.warning("Couldn't save JSON file")
