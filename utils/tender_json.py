import json
import os


def read_json(file_path):
    """Reads JSON data from a file and returns it as a dictionary."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(data, file_path):
    """Writes JSON data to a file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def update_json(tender_id, update_data, file_path):
    """Updates a specific tender in the JSON file."""
    data = read_json(file_path)
    if 'tenders' in data:
        if tender_id in data['tenders']:
            data['tenders'][tender_id].update(update_data)
            
        else:
            data['tenders'][tender_id]=update_data
        write_json(data, file_path)
    else:
        print(f"Tender ID {tender_id} not found.")