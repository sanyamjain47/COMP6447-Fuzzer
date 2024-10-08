"""
###########################
## JSON SPECIFIC METHODS ##
###########################
"""
import itertools

from copy import deepcopy

from library import PayloadJson
import random
import itertools
import threading
from harness import run_binary_string, run_strings
from queue import Queue
import time
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

def add_keywords(data: PayloadJson, keywords):
    """Strategy 0: keyword Strings
        find a random string field and edit value to keyword string
    """
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = random.choice(keywords)
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def more_keys(data: PayloadJson, _):
    """Add new key"""
    data.set_field("AAAA", "AAAA")
    return data


def nesting(data: PayloadJson, _):
    """Strategy 2: Nesting"""
    max_depth = 5 # CRITICAL: SET MAX DEPTH
    for i in range(max_depth):
        data.set_field(f"data{i}", [deepcopy(data.get_data())], update_keys=False)
    return data


def long_strings(data: PayloadJson, _):
    """Strategy 3: Long Strings
        find a random string field and edit value to long string
    """
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = "A"*10000
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def magic_numbers(data: PayloadJson, _):
    """Strategy 4: Numerical Extremes
        def strat4(data: dict, _):
    """
    keys_to_check = data.get_keys_of_type(int)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_values = [1e100, 1e9999, -1, 420.69, 999999999999999999999999, -999999999999, 0]
    updated_value = random.choice(updated_values)
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def large_keys(data: PayloadJson, _):
    """Strategy 5: Large Amount of Keys
    def strat5(data: dict, _):
    """
    for i in range(1000):
        data.set_field(f"key{i}", f"value{i}", update_keys=False)
    return data

# def strat6(data: dict, _):
#     """Strategy 6: Trailing Comma
#     def strat6(data: dict, _):
    
#     Trailing commas are not allowed in standard JSON, 
#     tests how JSON parsers handle non-standard input
#     """
#     key = list(data)[-1]

#     if (isinstance(str)): data[key] += ","
#     return data
    


def null_values(data: PayloadJson, _):
    """Strategy 7: send null values
        def strat7(data: dict, _):
    """
    keys_to_check = data.get_keys()
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, None)
    return data

def null_like_values(data: PayloadJson, _):
    """Strategy 9: send null-like values
        def strat9(data: dict, _):
    """
    keys_to_check = data.get_keys()
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    value = data.get_val(key_tup)
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
    data.set_field(key_tup, updated_value)
    return data

def fstrings(data: PayloadJson, _):
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, "%s%s%s%s")


def generate_json_fuzzed_output(df, q, keywords):
    json_mutator = [
        add_keywords,
        more_keys,
        nesting,
        long_strings,
        magic_numbers,
        large_keys,
        null_values,
        null_like_values,
        fstrings,
    ]

    for r in range(len(json_mutator)):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(json_mutator, r):  # All combinations of size r
            for _ in range(10):
                fuzzed_output = PayloadJson(df)
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output, keywords)  # Apply each mutator in the combination to the string
                json_string = str(fuzzed_output)
                q.put(json_string)

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

def loop_back_generator(input_queue,output_queue, all_mutations, keywords):
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
                    mutated_value = mutator(mutated_value, keywords)
                except:
                    continue
            mutated_values.append({"input": mutated_value, "mutator": mutator_combination})

        # Put the mutated values back into the queue
        for mutated_value_info in mutated_values:
            input_queue.put(mutated_value_info)

def multi_threaded_loop_back_generator(input_queue,output_queue, all_mutations, keywords, num_threads=5):
    threads = []

    def thread_target():
        loop_back_generator(input_queue,output_queue, all_mutations, keywords)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    return threads
