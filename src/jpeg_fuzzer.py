import random
import itertools
import random
import csv
import threading
from harness import run_binary_bytes
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

####################
## JPEG MUTATIONS ##
####################
    
def mutate_magic( data):
    # tuple = (byte-size of value, value)
    values = [
        (1, 0xff),
        (1, 0x7f),
        (1, 0),
        (2, 0xffff),
        (2, 0),
        (4, 0xffffffff),
        (4, 0),
        (4, 0x80000000),
        (4, 0x40000000),
        (4, 0x7fffffff)
    ]
    length = len(data) - 8  # make sure we dont write over the EOI marker
    idx = random.randint(0, length)
    n_size, n = random.choice(values)
    # print("magic mutate: ", idx, hex(n), n_size)
    if n_size == 1:
        if n == 0xff:			    # 0xFF
            data[idx] = 0xff        
        elif n == 0x7f:		        # 0x7F
            data[idx] = 0x7f
        elif n == 0:			    # 0x00
            data[idx] = 0
    elif n_size == 2:
        if n == 0xffff:			    # 0xFFFF
            data[idx] = 0xff
            data[idx + 1] = 0xff
        elif n == 0:			    # 0x0000
            data[idx] = 0
            data[idx + 1] = 0
    elif n_size == 4:
        if n == 0xFFFFFFFF:			# 0xFFFFFFFF
            data[idx] = 0xff
            data[idx + 1] = 0xff
            data[idx + 2] = 0xff
            data[idx + 3] = 0xff
        elif n == 0:			    # 0x00000000
            data[idx] = 0
            data[idx + 1] = 0
            data[idx + 2] = 0
            data[idx + 3] = 0
        elif n == 0x80000000:		# 0x80000000
            data[idx] = 0x80
            data[idx + 1] = 0
            data[idx + 2] = 0
            data[idx + 3] = 0
        elif n == 0x40000000:		# 0x40000000
            data[idx] = 0x40
            data[idx + 1] = 0
            data[idx + 2] = 0
            data[idx + 3] = 0
        elif n == 0x7FFFFFFF:		# 0x7FFFFFFF
            data[idx] = 0x7f
            data[idx + 1] = 0xff
            data[idx + 2] = 0xff
            data[idx + 3] = 0xff
    return data
      
    # randomly flip a proportion of bits

def flipRatioBits( data):
    length = len(data) - 4 #jpg file format requires SOI and EOI which are the first 2 and last 2 bytes. We don't want to touch them
    num_of_flips = int(length * 0.1)
    # print("flip bits ratio: ", ratio, num_of_flips)
    indexes = []
    flip_array = [1,2,4,8,16,32,64,128]
    while len(indexes) < num_of_flips:
        indexes.append(random.randint(0, length))
    for x in indexes:
        mask = random.choice(flip_array)
        data[x] = data[x] ^ mask
    if isinstance(data,int):
        print(f" ratio bits {type(data)}")
    return data
    
def flipRandomBit( data):
    # print("flip single bit")
    length = len(data) - 4 #jpg file format requires SOI and EOI which are the first 2 and last 2 bytes. We don't want to touch them
    idx = random.randint(0, length)
    flip_array = [1,2,4,8,16,32,64,128]
    mask = random.choice(flip_array)
    data[idx] = data[idx] ^ mask

    return data
    
def flipRandomByte( data):
    # print("flip single byte")
    length = len(data) - 4 #jpg file format requires SOI and EOI which are the first 2 and last 2 bytes. We don't want to touch them
    idx = random.randint(0, length)
    data[idx] = data[idx] ^ 0xff

    return data

def flipRatioBytes( data):
    length = len(data) - 4 #jpg file format requires SOI and EOI which are the first 2 and last 2 bytes. We don't want to touch them
    num_of_flips = int(length * 0.2)
    
    indexes = set()
    while len(indexes) < num_of_flips:
        indexes.add(random.randint(0, length))
    for idx in indexes:
        data[idx] = data[idx] ^ 0xff
    
    return data

def fuzz_soi(data):
    # Add random data after the SOI marker
    if len(data) >= 2:
        extra_data = bytearray(random.getrandbits(8) for _ in range(1000))  # Add 1000 bytes
        data = data[:2] + extra_data + data[2:]
    return data


def fuzz_quantization_tables(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xDB:
            # Inject a large quantization table
            large_table = bytearray(random.getrandbits(8) for _ in range(2000))  # 2000 bytes
            data = data[:i + 4] + large_table + data[i + 4:]
            i += 2004
        else:
            i += 1
    return data

def fuzz_sof(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xC0:
            extra_data = bytearray(random.getrandbits(8) for _ in range(1000))  # Add 1000 bytes
            data = data[:i + 4] + extra_data + data[i + 4:]
            i += 1004
        else:
            i += 1
    return data


def fuzz_huffman_tables(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xC4:
            large_table = bytearray(random.getrandbits(8) for _ in range(2000))  # 2000 bytes
            data = data[:i + 4] + large_table + data[i + 4:]
            i += 2004
        else:
            i += 1
    return data


def fuzz_image_data(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xDA:
            extra_data = bytearray(random.getrandbits(8) for _ in range(5000))  # Add 5000 bytes
            data = data[:i + 4] + extra_data + data[i + 4:]
            break
        else:
            i += 1
    return data
def fuzz_dqt(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xDB:
            large_table = bytearray(random.getrandbits(8) for _ in range(2000))  # 2000 bytes
            data = data[:i + 4] + large_table + data[i + 4:]
            i += 2004
        else:
            i += 1
    return data

def fuzz_dri(data):
    i = 0
    while i < len(data) - 2:
        if data[i] == 0xFF and data[i + 1] == 0xDD:
            extra_data = bytearray(random.getrandbits(8) for _ in range(1000))  # Add 1000 bytes
            data = data[:i + 4] + extra_data + data[i + 4:]
            i += 1004
        else:
            i += 1
    return data


def fuzz_jpeg_markers(data):
    markers_to_fuzz = [0xC0, 0xC4, 0xDA, 0xDB, 0xDD]  # SOF, DHT, Scan, DQT, DRI
    for i in range(len(data) - 1):
        if data[i] == 0xFF and data[i + 1] in markers_to_fuzz:
            data[i + 1] = random.choice(markers_to_fuzz)  # Swap with another marker
    return data

def fuzz_length_fields(data):
    for i in range(len(data) - 3):
        if data[i] == 0xFF:
            # Randomly change the length field
            length = (data[i + 2] << 8) | data[i + 3]
            fuzzed_length = random.randint(0, 0xFFFF)
            data[i + 2] = (fuzzed_length >> 8) & 0xFF
            data[i + 3] = fuzzed_length & 0xFF
    return data

def fuzz_exif_data(data):
    exif_marker = b'\xFF\xE1'
    # Insert a random EXIF marker
    insert_position = random.randint(2, len(data) - 1)
    data = data[:insert_position] + exif_marker + b'\x00\x10' + bytearray(random.getrandbits(8) for _ in range(16)) + data[insert_position:]
    return data

def fuzz_overlapping_segments(data):
    i = 0
    while i < len(data) - 1:
        if data[i] == 0xFF:
            # Check if there are enough bytes left for the length field
            if i + 3 < len(data):
                length = (data[i + 2] << 8) | data[i + 3]
                if length > 1 and i + 2 + length < len(data):
                    cut_length = random.randint(1, length)
                    data = data[:i + 2 + cut_length] + data[i + 2 + length:]
                i += 2 + length
            else:
                break  # Not enough bytes left for a complete segment
        else:
            i += 1
    return data




def generate_jpeg_fuzzed_output(df, fuzzed_queue, binary_path, output_queue):
    jpeg_mutator = [
        flipRandomBit,
        flipRandomByte,
        flipRatioBits,
        flipRatioBytes,
        mutate_magic,
        fuzz_soi,
        fuzz_quantization_tables,
        fuzz_sof,
        fuzz_huffman_tables,
        fuzz_image_data,
        fuzz_dqt,
        fuzz_dri,
        fuzz_jpeg_markers,
        fuzz_length_fields,
        fuzz_exif_data,
        fuzz_overlapping_segments,
    ]
    all_possible_mutations = Queue()
    list_all_possible_mutations = []
    
    
    for r in range(1, len(jpeg_mutator) + 1):
        for mutator_combination in itertools.combinations(jpeg_mutator, r):
            all_possible_mutations.put(mutator_combination)
            list_all_possible_mutations.append(mutator_combination)
    # Start generator threads
    generator_threads = multi_threaded_generator_csv(all_possible_mutations, df, fuzzed_queue, num_threads=20)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=20)


    loop_back_threads = multi_threaded_loop_back_generator(fuzzed_queue,output_queue, list_all_possible_mutations, num_threads=40)
    
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
                if isinstance(fuzzed_output,int):
                    print(type(fuzzed_output))
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
        run_binary_bytes(binary_path, fuzzed_queue, output_queue)
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
        fuzzed_output = None
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
        values_to_process = []
        if fuzzed_output is not None:
            values_to_process.append(fuzzed_output)
        values_to_process.append(output_queue.get()['input'])
        # Mutate each value with the chosen mutator combination
        mutated_values = []
        for value_info in values_to_process:
            mutated_value = random.choice([value_info, base_input])
            mutator_combination = random.choice(all_mutations)
            for mutator in mutator_combination:
                try:
                    mutated_value = mutator(mutated_value)
                except Exception as e:
                    print(f"Unexpected error loop: {e}")

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
