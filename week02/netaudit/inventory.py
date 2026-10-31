import json
from pathlib import Path


def load_json_file(file_path):
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)