import random
import itertools
import random
import csv
import threading
from harness import run_binary_string
from queue import Queue
from threading import Thread
import time
import string
##########################
## CSV SPECIFIC METHODS ##
##########################

def read_csv_to_list_of_lists(file_path):
    data = []
    try:
        with open(file_path, mode ='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return data

def csv_to_list_of_list(csv_string):
    lines = csv_string.split("\n")
    list_of_list = [line.split(",") for line in lines]
    return list_of_list

def inconsistent_data_types(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = str(lst_lst[row][col]) + 'abc'
    return lst_lst

def negative_numbers(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, len(lst_lst[row]) - 1)
        # Check if the value is a number before applying abs()
        if isinstance(lst_lst[row][col], (int, float)):
            lst_lst[row][col] = -abs(lst_lst[row][col])
        else:
            # Handle the case where the value is not a number
            # You might choose to skip, log a warning, or handle it differently
            pass
    return lst_lst



def foreign_characters(lst_lst, mutation_count=10):
    foreign_chars = ['你', '好', '안', '녕', 'こんにちは', 'م', 'λ', 'Φ', 'Ж', 'א', 'ß', 'Ñ']
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        num_chars = random.randint(1, 10)
        random_chars = ''.join(random.choices(foreign_chars, k=num_chars))
        lst_lst[row][col] = random_chars
    return lst_lst


def extra_commas(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = str(lst_lst[row][col]) + ',,,'
    return lst_lst


def nested_quotes(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = '"' + str(lst_lst[row][col]) + '"'
    return lst_lst


def add_many_rows(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    for _ in range(mutation_count):
        num_new_rows = random.randint(100, 200)
        row_to_duplicate = random.randint(0, num_rows - 1)
        for _ in range(num_new_rows):
            lst_lst.append(lst_lst[row_to_duplicate][:])
    return lst_lst

def extreme_numeric_values(lst_lst, mutation_count=10):
    extreme_values = [2**31-1, -2**31, 2**63-1, -2**63, float('inf'), float('-inf')]
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = random.choice(extreme_values)
    return lst_lst

def format_string_vulnerabilities(lst_lst, mutation_count=10):
    format_strings = ['%s', '%x', '%n', '%p', '%d']
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = random.choice(format_strings)
    return lst_lst

def long_strings(lst_lst, mutation_count=10, string_length=10000):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        long_string = ''.join(random.choices(string.ascii_letters + string.digits, k=string_length))
        lst_lst[row][col] = long_string
    return lst_lst

def null_byte_injection(lst_lst, mutation_count=10):
    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = '\0' + str(lst_lst[row][col])
    return lst_lst

def recursive_nesting(lst_lst, mutation_count=10, depth=10):
    def nest(value, level):
        if level == 0:
            return value
        return [nest(value, level - 1)]

    num_rows = len(lst_lst)
    num_cols = len(lst_lst[0])
    for _ in range(mutation_count):
        row = random.randint(0, num_rows - 1)
        col = random.randint(0, num_cols - 1)
        lst_lst[row][col] = nest(lst_lst[row][col], depth)
    return lst_lst


def list_of_lists_to_csv(lst_lst):
    csv_string = ""
    for row in lst_lst:
        row_str = [str(item) for item in row]
        csv_row = ",".join(row_str)
        csv_string += csv_row + "\n"
    return csv_string

def generate_csv_fuzzed_output(df, fuzzed_queue, binary_path):
    csv_mutator = [
        inconsistent_data_types,
        negative_numbers,
        foreign_characters,
        extra_commas,
        nested_quotes,
        add_many_rows,
        extreme_numeric_values,
        format_string_vulnerabilities,
        long_strings,
        null_byte_injection,
        recursive_nesting
    ]
    df = csv_to_list_of_list(df)
    all_possible_mutations = Queue()
    for count in range(10):
        for r in range(1, len(csv_mutator) + 1):
            for mutator_combination in itertools.combinations(csv_mutator, r):
                all_possible_mutations.put(mutator_combination)
    print(all_possible_mutations.qsize())

    # Start generator threads
    generator_threads = multi_threaded_generator_csv(all_possible_mutations, df, fuzzed_queue, num_threads=1)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=1)

    # Wait for all generator and harness threads to complete
    for thread in generator_threads + harness_threads:
        thread.join()

def multi_threaded_generator_csv(mutator_queue, input, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        generator_csv(mutator_queue, input, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads  # Return the list of threads instead of joining them here

def multi_threaded_harness(binary_path, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        run_binary_string(binary_path, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads

def generator_csv(mutator_queue, input, fuzzed_queue):
    while True:
        if not mutator_queue.empty():
            mutator_combination = mutator_queue.get()
            fuzzed_output = input
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
            csv_string = list_of_lists_to_csv(fuzzed_output)
            fuzzed_queue.put({"input":csv_string,"mutator":mutator_combination})
        else:

            return


# Test it out
if __name__ == "__main__":

    df = read_csv_to_list_of_lists("../assignment/csv1.txt")
    temp = add_many_rows(df)
    csv_string = list_of_lists_to_csv(temp)
    # print(csv_string)
    run_binary_and_check_segfault("../assignment/csv1",csv_string)
#    generate_csv_fuzzed_output(df)
