import itertools
from queue import Queue
import random
import subprocess
import sys
from pwn import *
from harness import run_binary_and_check_segfault
from queue import Queue
from threading import Thread
import struct

##########################
## JPEG SPECIFIC METHODS ##
##########################

def corrupt_header(jpeg_bytes):
    header_length = 10  # Change as needed
    for i in range(2, header_length):
        jpeg_bytes[i] = random.randint(0, 255)
    return jpeg_bytes

def insert_random_bytes(jpeg_bytes):
    # Insert random bytes at a random position
    position = random.randint(2, len(jpeg_bytes) - 1)
    random_bytes = [random.randint(0, 255) for _ in range(random.randint(1, 5))]
    return jpeg_bytes[:position] + bytearray(random_bytes) + jpeg_bytes[position:]

def remove_random_bytes(jpeg_bytes):
    # Remove a sequence of bytes from a random position
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        length = random.randint(1, 5)
        return jpeg_bytes[:position] + jpeg_bytes[position + length:]
    return jpeg_bytes

def flip_random_bits(jpeg_bytes):
    # Flip a random bit in the file
    byte_index = random.randint(0, len(jpeg_bytes) - 1)
    bit_index = random.randint(0, 7)
    byte_list = list(jpeg_bytes)
    byte_list[byte_index] ^= 1 << bit_index
    return bytearray(byte_list)

def generate_jpeg_fuzzed_output(jpeg_bytes, fuzzed_queue, binary_path):
    jpeg_mutators = [
        corrupt_header,
        insert_random_bytes,
        remove_random_bytes,
        flip_random_bits,
    ]

    #TODO Remove this - Testing code only
    with open(jpeg_path, 'rb') as file:
        jpeg_bytes = bytearray(file.read())

    all_possible_mutations = Queue()
    for count in range(10):  # Adjust this count as needed
        for r in range(1, len(jpeg_mutators) + 1):
            for mutator_combination in itertools.combinations(jpeg_mutators, r):
                all_possible_mutations.put(mutator_combination)

    # Start generator threads
    generator_threads = multi_threaded_generator_jpeg(all_possible_mutations, jpeg_bytes, fuzzed_queue, num_threads=10)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=10)

    # Wait for all generator and harness threads to complete
    for thread in generator_threads + harness_threads:
        thread.join()

def multi_threaded_generator_jpeg(mutator_queue, input_jpeg, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        generator_jpeg(mutator_queue, input_jpeg, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads

def generator_jpeg(mutator_queue, input_jpeg, fuzzed_queue):
    while True:
        if not mutator_queue.empty():
            mutator_combination = mutator_queue.get()
            fuzzed_output = input_jpeg[:]
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)
            fuzzed_queue.put({"input": fuzzed_output, "mutator": mutator_combination})
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

if __name__ == "__main__":
    q = Queue()
    jpeg_path = '../assignment/jpg1.txt'
    generate_jpeg_fuzzed_output(jpeg_path, q, "../assignment/jpg1")
