import json
import os

def read_json(file_path):
    """Reads a JSON file and returns the data."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(file_path, data):
    """Writes data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_json(file_path, key, value):
    """Updates a specific key in the JSON file with the provided value."""
    data = read_json(file_path)
    data[key] = value
    write_json(file_path, data)