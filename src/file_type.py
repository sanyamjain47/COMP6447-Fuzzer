import json
import csv
import os
import xml.etree.ElementTree as et

def read_and_determine_data(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    file_type = determine_input_type(content)

    if file_type == 'JSON':
        json_data = json.loads(content)
        return json.dumps(json_data), "JSON"
    elif file_type == 'CSV':
        csv_reader = csv.DictReader(content.splitlines())
        csv_data = [row for row in csv_reader]
        csv_fieldnames = csv_reader.fieldnames
        output = []
        if csv_fieldnames:
            output.append(','.join(csv_fieldnames))
        for row in csv_data:
            output.append(','.join([str(row[field]) for field in csv_fieldnames]))
        return '\n'.join(output),"CSV"
    elif file_type == 'XML':
        return content, "XML"
    else:
        return content,"Plaintext"

def determine_input_type(input_string):
    try:
        json.loads(input_string)
        return "JSON"
    except ValueError:
        pass

    try:
        root = et.fromstring(input_string)
        return "XML"
    except et.ParseError:
        pass

    try:
        csv_reader = csv.reader(input_string.splitlines())
        for _ in csv_reader:
            break  # If reading as CSV succeeds even for one line, it's considered valid
        if "," in input_string.splitlines()[0]:
            return "CSV"
    except csv.Error:
        pass

    return "Plaintext"

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
