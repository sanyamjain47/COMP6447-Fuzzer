import json
import csv
import imghdr

def read_and_determine_data(file_path):
    # First, try reading the file as binary to check if it's an image
    with open(file_path, 'rb') as f:
        binary_content = f.read()
        file_type = determine_input_type(binary_content, binary=True)
        if file_type == "JPEG":
            return binary_content, file_type

    # If not an image, read as a text file
    with open(file_path, 'r') as f:
        text_content = f.read()
        file_type = determine_input_type(text_content)
        return process_text_content(text_content, file_type)

def process_text_content(content, file_type):
    if file_type == 'JSON':
        json_data = json.loads(content)
        return json.dumps(json_data, indent=4), "JSON"
    elif file_type == 'CSV':
        csv_reader = csv.DictReader(content.splitlines())
        csv_data = [row for row in csv_reader]
        csv_fieldnames = csv_reader.fieldnames
        output = []
        if csv_fieldnames:
            output.append(','.join(csv_fieldnames))
        for row in csv_data:
            output.append(','.join([str(row[field]) for field in csv_fieldnames]))
        return '\n'.join(output), "CSV"
    else:
        return content, "Plaintext"

def determine_input_type(input_content, binary=False):
    if binary:
        file_type = imghdr.what(None, h=input_content)
        if file_type in ['jpeg', 'jpg']:
            return "JPEG"
        else:
            return "Unknown binary format"
    else:
        try:
            json.loads(input_content)
            return "JSON"
        except ValueError:
            pass

        try:
            csv.reader(input_content.splitlines())
            return "CSV"
        except csv.Error:
            pass

        return "Plaintext"
    
import os

def file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)

def has_permissions(file_path: str, mode: str) -> bool:
    permission_flags = {
        'r': os.R_OK,
        'w': os.W_OK,
        'x': os.X_OK
    }
    return os.access(file_path, permission_flags.get(mode, 0))

def check_file(file_path:str, mode: str) -> bool:
    if not file_exists(file_path):
        print(f" {file_path} doesn't exist")
        return False
    if not has_permissions(file_path, mode):
        print(f"{file_path} doesn't have appropriate permissions")
        return False
    return True