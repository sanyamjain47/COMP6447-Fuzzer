"""
###########################
## JSON SPECIFIC METHODS ##
###########################
"""
import itertools

from copy import deepcopy
from library import PayloadJson
import random
from harness import run_binary_and_check_segfault
from queue import Queue
from threading import Thread
import threading

def more_keys(data: PayloadJson):
    """Add new key"""
    data.set_field("AAAA", "AAAA")
    return data


def nesting(data: PayloadJson):
    """Strategy 2: Nesting"""
    max_depth = 5 # CRITICAL: SET MAX DEPTH
    for i in range(max_depth):
        data.set_field(f"data{i}", [deepcopy(data.get_data())], update_keys=False)
    return data

def long_strings(data: PayloadJson):
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

def magic_numbers(data: PayloadJson):
    """Strategy 4: Numerical Extremes
        def strat4(data: dict):
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

def large_keys(data: PayloadJson):
    """Strategy 5: Large Amount of Keys
    def strat5(data: dict):
    """
    for i in range(1000):
        data.set_field(f"key{i}", f"value{i}", update_keys=False)
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
    


def null_values(data: PayloadJson):
    """Strategy 7: send null values
        def strat7(data: dict):
    """
    keys_to_check = data.get_keys()
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, None)
    return data

def null_like_values(data: PayloadJson):
    """Strategy 9: send null-like values
        def strat9(data: dict):
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

def fstrings(data: PayloadJson):
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, "%s%s%s%s")
    

def generate_json_fuzzed_output(df, fuzzed_queue, binary_path):
    json_mutator = [
        more_keys,
        nesting,
        long_strings,
        magic_numbers,
        large_keys,
        null_values,
        null_like_values,
    ]

    all_possible_mutations = Queue()
    for count in range(10):
        for r in range(1, len(json_mutator) + 1):
            for mutator_combination in itertools.combinations(json_mutator, r):
                all_possible_mutations.put(mutator_combination)

    # Start generator threads
    generator_threads = multi_threaded_generator_json(all_possible_mutations, df, fuzzed_queue, num_threads=1)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=1)

    # Wait for all generator and harness threads to complete
    for thread in generator_threads + harness_threads:
        thread.join()

def multi_threaded_generator_json(mutator_queue, input, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        generator_json(mutator_queue, input, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads

def generator_json(mutator_queue, input, fuzzed_queue):
    while True:
        if not mutator_queue.empty():
            mutator_combination = mutator_queue.get()
            fuzzed_output = PayloadJson(input)  # Assuming PayloadJson is a class or function that prepares the JSON payload
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)
            json_string = fuzzed_output.output()  # Assuming output() method returns the JSON string
            fuzzed_queue.put({"input":json_string,"mutator":mutator_combination})
        else:
            return

def multi_threaded_harness(binary_path, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        run_binary_and_check_segfault(binary_path, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads