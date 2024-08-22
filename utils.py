import json


def load_json_body(filepath):
    with open(filepath, "r") as file:
        return json.load(file)
