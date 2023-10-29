import random
import itertools
import random
from io import StringIO
import csv
##########################
## CSV SPECIFIC METHODS ##
##########################


def inconsistent_data_types(lst_lst):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    row = random.randint(0, num_rows - 1)
    col = random.randint(0, num_cols - 1)
    lst_lst[row][col] = str(lst_lst[row][col]) + 'abc'
    return lst_lst

def negative_numbers(lst_lst):
    num_rows = len(lst_lst)
    numeric_cols = [i for i, val in enumerate(lst_lst[0]) if isinstance(val, (int, float))]
    if not numeric_cols:
        return lst_lst
    col = random.choice(numeric_cols)
    row = random.randint(0, num_rows - 1)
    lst_lst[row][col] = -abs(lst_lst[row][col])
    return lst_lst

def foreign_characters(lst_lst):
    foreign_chars = ['你', '好', '안', '녕', 'こんにちは', 'م', 'λ', 'Φ', 'Ж', 'א', 'ß', 'Ñ']
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    row = random.randint(0, num_rows - 1)
    col = random.randint(0, num_cols - 1)
    num_chars = random.randint(1, 10)
    random_chars = ''.join(random.choices(foreign_chars, k=num_chars))
    lst_lst[row][col] = random_chars
    return lst_lst

def extra_commas(lst_lst):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    row = random.randint(0, num_rows - 1)
    col = random.randint(0, num_cols - 1)
    lst_lst[row][col] = str(lst_lst[row][col]) + ',,,'
    return lst_lst

def nested_quotes(lst_lst):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    row = random.randint(0, num_rows - 1)
    col = random.randint(0, num_cols - 1)
    lst_lst[row][col] = '"' + str(lst_lst[row][col]) + '"'
    return lst_lst

# Adding rows or columns in a list-of-lists can be resource-intensive due to the need to copy existing data.
# Here's a simple example for adding rows:

def add_many_rows(lst_lst):
    num_rows = len(lst_lst)
    num_new_rows = random.randint(1000, 5000)
    row_to_duplicate = random.randint(0, num_rows - 1)
    for _ in range(num_new_rows):
        lst_lst.append(lst_lst[row_to_duplicate][:])
    return lst_lst



def list_of_lists_to_csv(lst_lst):
    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerows(lst_lst)
    return output.getvalue()



def generate_csv_fuzzed_output(df):
    csv_mutator = [
        inconsistent_data_types,
        negative_numbers,
        foreign_characters,
        extra_commas,
        nested_quotes,
        add_many_rows,
    ]
    all_mets = set()
    for r in range(1, len(csv_mutator) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(csv_mutator, r):  # All combinations of size r
            fuzzed_output = df
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                # ADD THIS TO QUEUE # TODO
            csv_string = list_of_lists_to_csv(fuzzed_output)
            if len(mutator_combination) == 1:
                print("***")
                print(csv_string)
                print("***")
            all_mets.add(mutator_combination)
    print(all_mets)

# Test it out
if __name__ == "__main__":

    df = [
    ['Name', 'Age', 'Occupation'],
    ['Alice', 28, 'Engineer'],
    ['Bob', 34, 'Doctor'],
    ['Charlie', 45, 'Teacher'],
    ['David', 23, 'Artist']
]   

    print(df)

    generate_csv_fuzzed_output(df)
