import random
import itertools
from queue import Queue
from pwn import log
import threading
import time
from harness import run_binary_string
from queue import Queue
from threading import Thread
import time
import string


# Global flag to indicate whether to terminate threads
terminate_threads_flag = False

# thread-safe int
function_count_lock = threading.Lock()
first_count = -1
base_input = None


###################
## BASIC METHODS ##
###################

# Flips 1-8 bits of a character in a string (bit or byte flipping)
def bit_flip(s: str):
    if not s:
        return s

    pos = random.randint(0, len(s) - 1)
    char = s[pos]
    bits_to_flip = random.randint(1, 7)
    for _ in range(bits_to_flip):
        bit = 1 << random.randint(0, 6)
        char = chr(ord(char) ^ bit)
    return s[:pos] + char + s[pos+1:]


# Deletes a random character from the string
def delete_random_byte(s: str):
    if not s:
        return s

    pos = random.randint(0, len(s) - 1)
    length = random.randint(1, len(s) - pos)
    return s[:pos] + s[pos+length:]


def insert_random_byte(s: str):
    pos = random.randint(0, len(s))
    length = random.randint(1, 10)
    random_bytes = ''.join(chr(random.randrange(32,127)) for _ in range(length))
    return s[:pos] + random_bytes + s[pos:]


# Adds a random number of characters to the end of the text files
def append_random_num_bytes(s: str):
    if not s:
        return s

    num_bytes = random.randint(1, 50)
    random_char = chr(random.randrange(32,127))
    return s + (num_bytes * random_char)


# To the end of the input, appends a substring, x number of times
# this breaks csv1 after a number of runs
def append_random_num_str(s: str):
    if not s:
        return s

    lower_bound = random.randint(0, len(s) - 1)
    upper_bound = random.randint(lower_bound, len(s))
    multiplier = random.randint(1, 10)
    return s + (s[lower_bound: upper_bound] * multiplier)

def generate_base_fuzzed_output(s: str, fuzzed_queue, binary_path, output_queue):
    base_mutators = [
        delete_random_byte,
        insert_random_byte,
        bit_flip,
        append_random_num_bytes,
        append_random_num_str
    ]
    all_possible_mutations = Queue()
    list_all_possible_mutations = []
    for count in range(10):
        for r in range(1, len(base_mutators) + 1):
            for mutator_combination in itertools.combinations(base_mutators, r):
                all_possible_mutations.put(mutator_combination)
                list_all_possible_mutations.append(mutator_combination)
    
    # Start generator threads
    generator_threads = multi_threaded_generator_csv(all_possible_mutations, s, fuzzed_queue, num_threads=2)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=2)


    loop_back_threads = multi_threaded_loop_back_generator(fuzzed_queue,output_queue, list_all_possible_mutations, num_threads=2)
    
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
                fuzzed_queue.put({"input": fuzzed_output, "mutator": mutator_combination})
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
