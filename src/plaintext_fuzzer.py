"""
###########################
## plaintext SPECIFIC METHODS ##
###########################
"""
import itertools
from queue import Queue
from random import randint, choice
from re import findall
import threading
import time
import random

from harness import run_binary_string
# Global flag to indicate whether to terminate threads
terminate_threads_flag = False

# thread-safe int
function_count_lock = threading.Lock()
first_count = -1
base_input = None

def increment_random_number(s: str, _):
    numbers = findall(r'\d+', s)

    if not numbers:
        return s

    random_number = choice(numbers)
    incremented_number = str(int(random_number) + 1)
    return s.replace(random_number, incremented_number, 1)

def decrement_random_number(s: str, _):
    numbers = findall(r'\d+', s)

    if not numbers:
        return s

    random_number = choice(numbers)
    incremented_number = str(int(random_number) - 1)
    return s.replace(random_number, incremented_number, 1)

def increment_random_byte(s: str, _):
    if not s:
        return s

    pos = randint(0, len(s)-1)
    return s[:pos] + chr(ord(s[pos])+1) + s[pos+1:]

def decrement_random_byte(s: str, _):
    if not s:
        return s
    pos = randint(0, len(s)-1)
    
    return s[:pos] + chr(ord(s[pos])-1) + s[pos+1:]

def bit_flip(s: str, _):
    if not s:
        return s
    pos = randint(0, len(s) - 1)
    char = s[pos]
    bits_to_flip = randint(1, 7)
    for _ in range(bits_to_flip):
        bit = 1 << randint(0, 6)
        char = chr(ord(char) ^ bit)
    return s[:pos] + char + s[pos+1:]

def replace_with_keyword(_, keywords):
    return choice(keywords)

def append_keyword(s: str, keywords):
    return s + choice(keywords)

def null_byte(s: str, _):
    return s + "\x00"

def new_line(s: str, _):
    return s + "\n"

def special_char(s: str, _):
    specials = ["~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", "]", "[", "|", "\\", "`", ",", ".", "/", "?", ";", ":", "'", "<"]
    return s + choice(specials)
    

def f_string(s: str, _):
    return s + "%s%s%s%s%s%s"

def extend(s: str, _):
    return s + "A" * 127

def double_it(s: str, _):
    return s + s

def generate_plain_fuzzed_output(df, fuzzed_queue, binary_path, output_queue, keywords):
    plain_mutator = [
        decrement_random_byte,
        increment_random_byte,
        decrement_random_number,
        increment_random_number,
        bit_flip,
        replace_with_keyword,
        append_keyword,
        null_byte,
        new_line,
        special_char,
        f_string,
        extend,
        double_it,
    ]

    all_possible_mutations = Queue()
    list_all_possible_mutations = []
    for count in range(10):  # Adjust this count as needed
        for r in range(1, len(plain_mutator) + 1):
            for mutator_combination in itertools.combinations(plain_mutator, r):
                all_possible_mutations.put(mutator_combination)
                list_all_possible_mutations.append(mutator_combination)

    
    # Start generator threads
    generator_threads = multi_threaded_generator_txt(all_possible_mutations, df, fuzzed_queue, keywords, num_threads=20)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=20)


    loop_back_threads = multi_threaded_loop_back_generator(fuzzed_queue,output_queue, list_all_possible_mutations, num_threads=10)
    
    for thread in generator_threads + harness_threads + loop_back_threads:
        thread.join()

def multi_threaded_generator_txt(mutator_queue, input, fuzzed_queue, keywords, num_threads=5):
    threads = []

    def thread_target():
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
                    fuzzed_output = mutator(fuzzed_output, keywords)  # Apply each mutator in the combination to the string
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
