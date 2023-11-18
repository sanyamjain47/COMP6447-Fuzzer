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
def flip_bits(byte_input):
    ratio = 0.00001  # Example ratio, adjust as needed
    length = len(byte_input) - 4
    num_of_flips = int(length * ratio)
    flip_array = [1, 2, 4, 8, 16, 32, 64, 128]

    for _ in range(num_of_flips):
        idx = random.randint(0, length)
        mask = random.choice(flip_array)
        byte_input[idx] ^= mask

    return byte_input

def random_header_modification(byte_input):
    length = len(byte_input) - 4
    idx = random.randint(0, length)
    byte_input[idx] ^= random.randint(0, 255)
    return byte_input

def insert_random_marker(byte_input):
    markers = [0xd8, 0xe0, 0xe1]  # Example markers, adjust as needed
    position = random.randint(2, len(byte_input) - 2)
    marker = random.choice(markers)
    return byte_input[:position] + bytes([marker]) + byte_input[position:]


def swap_segments(byte_input):
    seg1_start = random.randint(0, len(byte_input) // 2)
    seg1_end = seg1_start + random.randint(2, 20)
    seg2_start = random.randint(len(byte_input) // 2, len(byte_input) - 20)
    seg2_end = seg2_start + random.randint(2, 20)

    byte_input[seg1_start:seg1_end], byte_input[seg2_start:seg2_end] = \
        byte_input[seg2_start:seg2_end], byte_input[seg1_start:seg1_end]

    return byte_input

def random_block_shuffle(byte_input):
    block_size = 64  # 8x8 block
    num_blocks = len(byte_input) // block_size
    blocks = [byte_input[i * block_size:(i + 1) * block_size] for i in range(num_blocks)]
    random.shuffle(blocks)
    return b''.join(blocks)

def random_metadata_insertion(byte_input):
    exif_header = b'\xff\xe1' + struct.pack('>H', random.randint(2, 100))
    random_metadata = bytes([random.randint(0, 255) for _ in range(random.randint(1, 20))])
    return exif_header + random_metadata + byte_input

def mutate_magic(data):
    values = [
        (1, 0xff), (1, 0x7f), (1, 0),
        (2, 0xffff), (2, 0),
        (4, 0xffffffff), (4, 0), (4, 0x80000000), (4, 0x40000000), (4, 0x7fffffff)
    ]
    length = len(data) - 8
    idx = randint(0, length)
    n_size, n = random.choice(values)

    data[idx:idx+n_size] = n.to_bytes(n_size, 'little')
    return data

def flip_ratio_bits(data, ratio):
    length = len(data) - 4
    num_of_flips = int(length * ratio)
    flip_array = [1, 2, 4, 8, 16, 32, 64, 128]

    for _ in range(num_of_flips):
        idx = randint(0, length)
        mask = random.choice(flip_array)
        data[idx] ^= mask

    return data

def flip_random_bit(data):
    length = len(data) - 4
    idx = randint(0, length)
    flip_array = [1, 2, 4, 8, 16, 32, 64, 128]
    mask = random.choice(flip_array)
    data[idx] ^= mask

    return data

def flip_random_byte(data):
    length = len(data) - 4
    idx = randint(0, length)
    data[idx] ^= 0xff

    return data


# Fuzzing generator
def generator_jpeg(mutator_queue, input_jpeg, fuzzed_queue):
    while not mutator_queue.empty():
        mutator_combination = mutator_queue.get()
        fuzzed_output = input_jpeg[:]
        for mutator in mutator_combination:
            fuzzed_output = mutator(fuzzed_output)
        fuzzed_queue.put({"input": fuzzed_output, "mutator": mutator_combination})

# Thread management for fuzzing
def multi_threaded_generator_jpeg(mutator_queue, input_jpeg, fuzzed_queue, num_threads=5):
    threads = [threading.Thread(target=generator_jpeg, args=(mutator_queue, input_jpeg, fuzzed_queue)) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    return threads

def multi_threaded_harness(binary_path, fuzzed_queue, num_threads=5):
    threads = [threading.Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_queue)) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    return threads

# Main fuzzing function
def generate_jpeg_fuzzed_output(jpeg_path, fuzzed_queue, binary_path):
    with open(jpeg_path, 'rb') as file:
        jpeg_bytes = bytearray(file.read())

    jpeg_mutators = [flip_bits, random_header_modification, insert_random_marker, swap_segments, random_block_shuffle, random_metadata_insertion]
    all_possible_mutations = Queue()

    for _ in range(20):
        for r in range(1, len(jpeg_mutators) + 1):
            for mutator_combination in itertools.combinations(jpeg_mutators, r):
                all_possible_mutations.put(mutator_combination)

    generator_threads = multi_threaded_generator_jpeg(all_possible_mutations, jpeg_bytes, fuzzed_queue, num_threads=20)
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=20)

    for thread in generator_threads + harness_threads:
        thread.join()

if __name__ == "__main__":
    q = Queue()
    jpeg_path = '../assignment/jpg1.txt'
    generate_jpeg_fuzzed_output(jpeg_path, q, "../assignment/jpg1")
