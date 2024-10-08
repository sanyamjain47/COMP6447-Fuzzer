"""
# Example usage
input_csv_file = "input.csv"
output_dir = "fuzzed_csvs"
fuzz_csv(input_csv_file, output_dir)
"""
import csv
import json
import random
import os

from library.helpers import get_dict_all_keys, get_dict_all_keys_of_type, update_nested_dict

def fuzz_csv(input_csv_file, output_dir, num_fuzzed_files=10):
    """
    Fuzz a CSV file and generate 'num_fuzzed_files' number of fuzzed CSV files.
    Parameters:
        - input_csv_file: The path to the input CSV file.
        - output_dir: Directory to store fuzzed CSV files.
        - num_fuzzed_files: Number of fuzzed CSV files to generate.
    """
    # Read the original CSV content
    with open(input_csv_file, mode='r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0]
    rows = rows[1:]
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Start generating fuzzed files
    for i in range(num_fuzzed_files):
        fuzzed_rows = list(rows)  # Clone original rows
        # Strategy 1: Byte flips
        if random.choice([True, False]):
            row_idx, col_idx = random.randint(0, len(fuzzed_rows) - 1), random.randint(0, len(header) - 1)
            fuzzed_rows[row_idx][col_idx] = fuzzed_rows[row_idx][col_idx][::-1]  # Reverse string
        # Strategy 2: Add a lot of rows
        if random.choice([True, False]):
            new_row = random.choice(fuzzed_rows)
            for _ in range(random.randint(1, 10)):  # Add 1-10 new rows
                fuzzed_rows.append(new_row)
        # Strategy 3: Add a lot of columns
        if random.choice([True, False]):
            new_col_value = "fuzz"
            for row in fuzzed_rows:
                for _ in range(random.randint(1, 5)):  # Add 1-5 new columns
                    row.append(new_col_value)
        # Strategy 4: Mismatch the data type (replace digit with string or vice versa)
        if random.choice([True, False]):
            row_idx, col_idx = random.randint(0, len(fuzzed_rows) - 1), random.randint(0, len(header) - 1)
            cell_value = fuzzed_rows[row_idx][col_idx]
            if cell_value.isdigit():
                fuzzed_rows[row_idx][col_idx] = "fuzz"
            else:
                fuzzed_rows[row_idx][col_idx] = str(random.randint(0, 9999))
        # Write fuzzed CSV to file
        fuzzed_csv_file = os.path.join(output_dir, f'fuzzed_{i}.csv')
        with open(fuzzed_csv_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(fuzzed_rows)


def fuzz_json(data: dict) -> dict:
    """
    Fuzz a JSON.
    Parameters:
        - data: The dict of a input JSON.
    """

    if not data: 
        data = {
        "data": "AAAA"
        }

    # Start generating fuzzed files
    mutators = [
        strat1,
        strat2,
        strat3,
        strat4,
        strat5,
        strat7,
        strat9,
    ]
    mutator = random.choice(mutators)
    print(mutator)
    return mutator(data)


def strat1(data: dict):
    """Add new key"""
    data["AAAA"] = "AAAA"
    return data

# Strategy 2: Nesting
def strat2(data: dict):
    max_depth = 50 # CRITICAL: SET MAX DEPTH
    for _ in range(max_depth):
        data = {
            "data": [data]
            }
    return data

def strat3(data: dict):
    """Strategy 3: Long Strings
        find a random string field and edit value to long string
    """
    keys_to_check = get_dict_all_keys_of_type(data, str)
    key_tup = random.choice(keys_to_check)
    updated_value = "A"*10000
    value = data
    for key in key_tup:
        value = value[key]
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value

    update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat4(data: dict):
    """Strategy 4: Numerical Extremes
        def strat4(data: dict):
    """
    keys_to_check = get_dict_all_keys_of_type(data, int)
    key_tup = random.choice(keys_to_check)
    updated_values = [1e100, 1e9999, -1, 420.69, 999999999999999999999999, -999999999999, 0]
    updated_value = random.choice(updated_values)
    value = data
    for key in key_tup:
        value = value[key]
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value

    update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat5(data: dict):
    """Strategy 5: Large Amount of Keys
    def strat5(data: dict):
    """
    for i in range(1000):
        data[f"key{i}"] = f"value{i}"
    return data

# def strat6(data: dict):
#     """Strategy 6: Trailing Comma
#     def strat6(data: dict):
    
#     Trailing commas are not allowed in standard JSON, 
#     tests how JSON parsers handle non-standard input
#     """
#     key = list(data)[-1]

#     if (isinstance(str)): data[key] += ","
#     return data
    


def strat7(data: dict):
    """Strategy 7: send null values
        def strat7(data: dict):
    """
    keys_to_check = get_dict_all_keys(data)
    key_tup = random.choice(keys_to_check)
    updated_value = None
    update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat9(data: dict):
    """Strategy 9: send null-like values
        def strat9(data: dict):
    """
    keys_to_check = get_dict_all_keys(data)
    key_tup = random.choice(keys_to_check)
    value = data
    print(key_tup)
    for key in key_tup:
        value = value[key]
    if isinstance(value, list):
        updated_value = []
    elif isinstance(value, str):
        updated_value = ""
    elif isinstance(value, int):
        updated_value = 0
    elif isinstance(value, dict):
        updated_value = {}
    elif isinstance(value, float):
        updated_value = 0.0
    else:
        updated_value = None

    update_nested_dict(data, list(key_tup), updated_value)
    return data



if __name__ == "__main__":
    print(json.dumps(strat9({
        "len": 12,
        "input": "AAAABBBBCCCC",
        "more_data": ["a", "bb"],
        "again": {
            "len": 12,
            "input": "AAAABBBBCCCC",
            "more_data": ["a", "bb"],
            "again": {
                "len": 12,
                "input": "AAAABBBBCCCC",
                "more_data": ["a", "bb"],
            },
        }
    })))
