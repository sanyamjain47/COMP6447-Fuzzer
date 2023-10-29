import csv
import json
import random
import os
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
# Example usage
input_csv_file = "input.csv"
output_dir = "fuzzed_csvs"
fuzz_csv(input_csv_file, output_dir)


def fuzz_json(data: dict) -> dict:
    """
    Fuzz a JSON.
    Parameters:
        - data: The dict of a input JSON.
    """

    # if (json is empty): populate

    # Start generating fuzzed files
    mutators = [
        strat1,
        strat2,
        strat3,
    ]
    mutator = random.choice(mutators)
    print(mutator)
    return mutator(data)


# Strategy 1: Duplicate Keys
def strat1(data: dict):
    key = random.choice(list(data.keys()))

    # ensure different value for duplicate
    payload = "AAAA"
    if isinstance(data[key], str): payload = data[key] + "A"
    return data[key].append(payload)

# Strategy 2: Nesting
def strat2(data: dict):
    max_depth = 50 # CRITICAL: SET MAX DEPTH
    for _ in range(max_depth):
        data = {
            "data": [data]
            }
    return data

# Strategy 3: Long Strings
def strat3(data: dict):
    keys_to_check = list(data.keys())

    while keys_to_check:
        current_key = random.choice(keys_to_check)
        value = data.get(current_key)

        if isinstance(value, str): 
            data[current_key] = "A" * 100
            break
        elif isinstance(value, dict): keys_to_check.extend(value.keys())

        keys_to_check.remove(current_key)
        
    return data

# # Strategy 4: Numerical Extremes
# def strat4(data: dict):

