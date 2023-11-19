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

# Global flag to indicate whether to terminate threads
terminate_threads_flag = False

# thread-safe int
function_count_lock = threading.Lock()
first_count = -1
base_input = None

# Function to set the terminate flag
def set_terminate_flag():
    global terminate_threads_flag
    terminate_threads_flag = True

def generate_csv_fuzzed_output(df, fuzzed_queue, binary_path, output_queue):
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
    list_all_possible_mutations = []
    for count in range(10):
        for r in range(1, len(csv_mutator) + 1):
            for mutator_combination in itertools.combinations(csv_mutator, r):
                all_possible_mutations.put(mutator_combination)
                list_all_possible_mutations.append(mutator_combination)
    
    # Start generator threads
    generator_threads = multi_threaded_generator_csv(all_possible_mutations, df, fuzzed_queue, num_threads=20)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=20)


    loop_back_threads = multi_threaded_loop_back_generator(fuzzed_queue,output_queue, list_all_possible_mutations, num_threads=10)
    
    for thread in generator_threads + harness_threads + loop_back_threads:
        thread.join()
    

def multi_threaded_generator_csv(mutator_queue, input, fuzzed_queue, num_threads=5):
    threads = []

    def thread_target():
        count = 0
        start_time = time.time()
        time_limit = 160  # 150 seconds
        while True:
            new_time = time.time()
            if new_time - start_time > time_limit:
                return
            if not mutator_queue.empty():
                mutator_combination = mutator_queue.get()
                fuzzed_output = input
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                csv_string = list_of_lists_to_csv(fuzzed_output)
                fuzzed_queue.put({"input": csv_string, "mutator": mutator_combination})
            else:
                return

    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    
    return threads


def multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=5):
    threads = []

    def thread_target():
        run_binary_string(binary_path, fuzzed_queue, output_queue)
        return

    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    return threads

def loop_back_generator(input_queue,output_queue, all_mutations):
    global first_count
    global base_input
    start_time = time.time()
    time_limit = 160  # 150 seconds

    while True:
        
        new_time = time.time()
        if new_time - start_time > time_limit:
            return
        if output_queue.empty():
            time.sleep(5)
        with function_count_lock:
            fuzzed_output = output_queue.get()['input']
            function_count = output_queue.get()['count']

            if first_count == -1:
                first_count = function_count
                base_input = fuzzed_output


        # Take all values from the output queue
        values_to_process = list(output_queue.get()['input'])
        values_to_process.append(fuzzed_output)
        # Mutate each value with the chosen mutator combination
        mutated_values = []
        for value_info in values_to_process:
            mutated_value = random.choice([value_info,base_input])
            mutator_combination = random.choice(all_mutations)

            for mutator in mutator_combination:
                try:
                    mutated_value = mutator(mutated_value)
                except:
                    continue
            mutated_values.append({"input": mutated_value, "mutator": mutator_combination})

        # Put the mutated values back into the queue
        for mutated_value_info in mutated_values:
            input_queue.put(mutated_value_info)

def multi_threaded_loop_back_generator(input_queue,output_queue, all_mutations, num_threads=5):
    threads = []

    def thread_target():
        loop_back_generator(input_queue,output_queue, all_mutations)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    return threads
