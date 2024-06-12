import addict
from typing import Dict
import os
import json


class Config(addict.Dict):
    def __init__(self, config: Dict):
        super().__init__(**config)

    def merge_from_config(self, config):
        self.update(config)

    def merge_from_path(self, filepath: str):
        another_config = Config.from_file(filepath)
        self.merge_from_config(another_config)

    @staticmethod
    def from_file(filepath: str):
        if not os.path.exists(filepath):
            raise ValueError(f'File does not exists {filepath}')

        with open(filepath, 'r') as file:
            config = json.load(file)

        return Config(config)
