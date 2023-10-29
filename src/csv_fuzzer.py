import random
import itertools
import pandas as pd

##########################
## CSV SPECIFIC METHODS ##
##########################


def empty_cells(df):
    row = random.randint(0, df.shape[0]-1)
    col = random.randint(0, df.shape[1]-1)
    df.iat[row, col] = ''
    return df

def long_strings(df):
    row = random.randint(0, df.shape[0]-1)
    col = random.randint(0, df.shape[1]-1)
    df.iat[row, col] = 'a' * 5000
    return df

def special_characters(df):
    special_chars = ['\n', '\t', '\r']
    row = random.randint(0, df.shape[0]-1)
    col = random.randint(0, df.shape[1]-1)
    df.iat[row, col] = random.choice(special_chars) + str(df.iat[row, col])
    return df

def inconsistent_data_types(df):
    col = random.choice(df.columns)
    row = random.randint(0, df.shape[0]-1)
    df.iat[row, col] = str(df.iat[row, col]) + 'abc'
    return df

def header_manipulation(df):
    new_col = random.choice(df.columns) + '_new'
    df[new_col] = df[random.choice(df.columns)]
    return df

def negative_numbers(df):
    numeric_cols = df.select_dtypes(include=['number']).columns
    if numeric_cols.empty:
        return df
    col = random.choice(numeric_cols)
    row = random.randint(0, df.shape[0]-1)
    df.at[row, col] = -abs(df.at[row, col])
    return df

def foreign_characters(df):
    foreign_chars = ['你', '好', '안', '녕', 'こんにちは', 'م', 'λ', 'Φ', 'Ж', 'א', 'ß', 'Ñ']
    
    # Select random row and column
    row = random.randint(0, df.shape[0] - 1)
    col = random.randint(0, df.shape[1] - 1)
    
    num_chars = random.randint(1, 10)  # You can adjust the range
    random_chars = ''.join(random.choices(foreign_chars, k=num_chars))
    
    df.iat[row, col] = random_chars
    
    return df

def extra_commas(df):
    row = random.randint(0, df.shape[0]-1)
    col = random.choice(df.columns)
    df.at[row, col] = str(df.at[row, col]) + ',,,'
    return df

def nested_quotes(df):
    row = random.randint(0, df.shape[0]-1)
    col = random.randint(0, df.shape[1]-1)
    df.iat[row, col] = '"' + str(df.iat[row, col]) + '"'
    return df


def add_many_rows(df):
    num_rows = random.randint(1000, 5000)  # You can adjust these numbers
    new_rows = pd.DataFrame([df.iloc[random.randint(0, df.shape[0]-1)]] * num_rows).reset_index(drop=True)
    return pd.concat([df, new_rows]).reset_index(drop=True)

def add_many_columns(df):
    num_cols = random.randint(50, 200)  # You can adjust these numbers
    for i in range(num_cols):
        new_col_name = f'RandomCol_{i}'
        random_col = df[random.choice(df.columns)]
        df[new_col_name] = random_col
    return df

def duplicate_rows_and_columns(df):
    num_row_duplications = random.randint(5, 20)  # You can adjust these numbers
    num_col_duplications = random.randint(5, 20)  # You can adjust these numbers
    
    # Duplicate rows
    for _ in range(num_row_duplications):
        row = random.randint(0, df.shape[0]-1)
        df = pd.concat([df.iloc[:row], df.iloc[row:row+1], df.iloc[row:]], ignore_index=True)
        
    # Duplicate columns
    for _ in range(num_col_duplications):
        col = random.choice(df.columns)
        new_col_name = f'{col}_dup'
        df[new_col_name] = df[col]
        
    return df

# Combine rows and columns
def combine_rows_and_columns(df):
    # Double the rows
    df = pd.concat([df]*2).reset_index(drop=True)
    
    # Double the columns
    for col in df.columns:
        new_col_name = f'{col}_dup'
        df[new_col_name] = df[col]
        
    return df



def generate_csv_fuzzed_output(df):
    csv_mutator = [
        empty_cells,
        long_strings,
        special_characters,
        inconsistent_data_types,
        header_manipulation,
        negative_numbers,
        foreign_characters,
        extra_commas,
        nested_quotes,
        add_many_columns,
        add_many_rows,
        duplicate_rows_and_columns,
        combine_rows_and_columns
    ]
    #all_mets = set()
    for r in range(1, len(csv_mutator) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(csv_mutator, r):  # All combinations of size r
            for i in range(10): # 10 is a constant to run every type of combinartion atleast 10 times. Can be reduced
                fuzzed_output = df
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                    # ADD THIS TO QUEUE # TODO

                #all_mets.add(mutator_combination)
    #print(all_mets)

# Test it out
if __name__ == "__main__":
    generate_csv_fuzzed_output("test_string")
