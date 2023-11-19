import json
import csv
import os
import xml.etree.ElementTree as et
import magic

def read_and_determine_data(file_path):
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        content = f.read()

    file_type = determine_input_type(content)

    if file_type in ['JPEG', 'PDF']:
        return content, file_type
    elif file_type == 'JSON':
        # Decode content to string before processing
        json_data = json.loads(content.decode())
        return json.dumps(json_data), "JSON"
    elif file_type == 'CSV':
        content_decoded = content.decode()
        csv_reader = csv.DictReader(content_decoded.splitlines())
        csv_data = [row for row in csv_reader]
        csv_fieldnames = csv_reader.fieldnames
        output = []
        if csv_fieldnames:
            output.append(','.join(csv_fieldnames))
        for row in csv_data:
            output.append(','.join([str(row[field]) for field in csv_fieldnames]))
        return '\n'.join(output),"CSV"
    elif file_type == 'XML':
        return content.decode(), "XML"
    else:
        return content.decode(), "Plaintext"

def determine_input_type(input_bytes):
    # Use the magic library to determine the file type
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(input_bytes)

    if 'json' in file_type:
        return "JSON"
    elif 'csv' in file_type:
        return "CSV"
    elif 'jpeg' in file_type:
        return "JPEG"
    elif 'pdf' in file_type:
        return "PDF"
    elif 'xml' in file_type:
        return "XML"
    else:
        # Fallback check for XML
        try:
            et.fromstring(input_bytes)
            return "XML"
        except et.ParseError:
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