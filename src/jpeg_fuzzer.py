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

def modify_header(jpeg_bytes, negative=False):
    for i in range(2, 10):
        if negative:
            jpeg_bytes[i] = 0xFF + 1 + random.randint(-128, -1)
        else:
            jpeg_bytes[i] = random.randint(0, 255)
    return jpeg_bytes


def insert_bytes(jpeg_bytes, variable_length=False, negative=False):
    position = random.randint(2, len(jpeg_bytes) - 1)
    length = random.randint(1, 100) if variable_length else random.randint(1, 5)
    if negative:
        random_bytes = bytearray((0xFF + 1 + random.randint(-128, -1)) for _ in range(length))
    else:
        random_bytes = bytearray(random.randint(0, 255) for _ in range(length))
    return jpeg_bytes[:position] + random_bytes + jpeg_bytes[position:]


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

def swap_segments(jpeg_bytes):
    # Ensure the file is long enough to have multiple segments
    if len(jpeg_bytes) > 20:
        pos1 = random.randint(2, len(jpeg_bytes) // 2)
        pos2 = random.randint(len(jpeg_bytes) // 2, len(jpeg_bytes) - 1)
        segment1 = jpeg_bytes[pos1:pos1+5]
        segment2 = jpeg_bytes[pos2:pos2+5]
        jpeg_bytes[pos1:pos1+5], jpeg_bytes[pos2:pos2+5] = segment2, segment1
    return jpeg_bytes

def extend_segment_length(jpeg_bytes):
    # Ensure there's enough data to work with
    if len(jpeg_bytes) > 10:
        # Choose a random position in the data
        position = random.randint(2, len(jpeg_bytes) - 5)
        
        # Calculate a new length (ensure it's within the bounds of the data)
        new_length = random.randint(2, min(255, len(jpeg_bytes) - position - 1))

        # Convert the new length to bytes
        length_bytes = new_length.to_bytes(2, 'big')

        # Replace the segment length in the data
        # Make sure the slice you're replacing matches the size of length_bytes
        jpeg_bytes[position:position + len(length_bytes)] = length_bytes

    return jpeg_bytes

def truncate_segment_length(jpeg_bytes):
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        length_bytes = jpeg_bytes[position:position+2]
        length = max(1, int.from_bytes(length_bytes, 'big') - random.randint(1, 5))
        jpeg_bytes[position:position+2] = length.to_bytes(2, 'big')
    return jpeg_bytes

def randomize_segment_order(jpeg_bytes):
    # Assuming segments are of fixed length for simplicity
    segment_length = 10
    segments = [jpeg_bytes[i:i+segment_length] for i in range(0, len(jpeg_bytes), segment_length)]
    random.shuffle(segments)
    return bytearray().join(segments)

def inject_format_strings(jpeg_bytes):
    format_str = b'%s%p%x%n'
    position = random.randint(2, len(jpeg_bytes) - 1)
    return jpeg_bytes[:position] + format_str + jpeg_bytes[position:]

def duplicate_segment(jpeg_bytes):
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        segment = jpeg_bytes[position:position+5]
        return jpeg_bytes[:position] + segment + segment + jpeg_bytes[position:]
    return jpeg_bytes

def reverse_segment(jpeg_bytes):
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        segment = jpeg_bytes[position:position+5]
        jpeg_bytes[position:position+5] = segment[::-1]
    return jpeg_bytes


def inject_nop_sled(jpeg_bytes):
    nop_sled = b'\x90' * random.randint(10, 100)
    position = random.randint(2, len(jpeg_bytes) - 1)
    return jpeg_bytes[:position] + nop_sled + jpeg_bytes[position:]


def negative_length_segment(jpeg_bytes):
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        negative_length = -random.randint(1, 100)
        jpeg_bytes[position:position+2] = negative_length.to_bytes(2, byteorder='big', signed=True)
    return jpeg_bytes

def negative_byte_injection(jpeg_bytes):
    # Insert a sequence of 'negative' bytes at a random position
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        length = random.randint(1, 5)
        negative_bytes = bytearray((0xFF + 1 + random.randint(-128, -1)) for _ in range(length))
        return jpeg_bytes[:position] + negative_bytes + jpeg_bytes[position + length:]
    return jpeg_bytes

def negative_offset_in_headers(jpeg_bytes):
    for i in range(2, 10):
        # Convert negative value to unsigned byte representation
        jpeg_bytes[i] = 0xFF + 1 + random.randint(-128, -1)
    return jpeg_bytes

def negative_value_flip(jpeg_bytes):
    byte_index = random.randint(0, len(jpeg_bytes) - 1)
    # Convert negative value to unsigned byte representation
    jpeg_bytes[byte_index] = 0xFF + 1 + random.randint(-128, -1)
    return jpeg_bytes


def reverse_segment_negative(jpeg_bytes):
    if len(jpeg_bytes) > 10:
        position = random.randint(2, len(jpeg_bytes) - 5)
        segment = jpeg_bytes[position:position+5]
        segment_with_negatives = bytearray((0xFF + 1 + random.randint(-128, -1)) if random.random() < 0.5 else b for b in segment)
        jpeg_bytes[position:position+5] = segment_with_negatives[::-1]
    return jpeg_bytes




def generate_jpeg_fuzzed_output(jpeg_bytes, fuzzed_queue, binary_path):
    jpeg_mutators = [
        modify_header,
        insert_bytes,
        remove_random_bytes,
        flip_random_bits,
        swap_segments,
        extend_segment_length,
        truncate_segment_length,
        randomize_segment_order,
        inject_format_strings,
        duplicate_segment,
        reverse_segment,
        inject_nop_sled,
        negative_length_segment,
        negative_byte_injection,
        negative_offset_in_headers,
        negative_value_flip,
        reverse_segment_negative
    ]

    #TODO Remove this - Testing code only
    with open(jpeg_path, 'rb') as file:
        jpeg_bytes = bytearray(file.read())

    all_possible_mutations = Queue()
    for r in range(1, len(jpeg_mutators) + 1):
        for mutator_combination in itertools.combinations(jpeg_mutators, r):
            all_possible_mutations.put(mutator_combination)
    print(all_possible_mutations.qsize())
    # Start generator threads
    generator_threads = multi_threaded_generator_jpeg(all_possible_mutations, jpeg_bytes, fuzzed_queue, num_threads=20)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=20)

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
            print("done")
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
