import datetime
import json
import logging
import os
from pathlib import Path

script_dir = Path(os.path.dirname(os.path.realpath(__file__)))


class App:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
