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

def update_json(bidder_id, update_data, file_path):
    """Updates a specific tender in the JSON file."""
    data = read_json(file_path)
    if 'bidders' in data:
        if bidder_id in data['bidders']:
            data['bidders'][bidder_id].update(update_data)
            
        else:
            data['bidders'][bidder_id]=update_data
        write_json(file_path,data)
    else:
        print(f"Bidder ID {bidder_id} not found.")