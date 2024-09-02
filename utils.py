import json


def load_json_body(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
