from threading import Thread
from queue import Queue
from base_fuzzer import generate_base_fuzzed_output
from harness import run_binary_and_check_segfault
from csv_fuzzer import generate_csv_fuzzed_output
from json_fuzzer import generate_json_fuzzed_output


def start_csv(s: str, binary_path: str):
    fuzzed_input = Queue()

    # Start generating inputs in a separate thread
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    csvfuzz_generator_thread = Thread(target=generate_csv_fuzzed_output, args=(s, fuzzed_input))
    csvfuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    csvfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    binary_checker_thread.join()


def start_json(s: str, binary_path: str):
    fuzzed_input = Queue()

    # Start generating inputs in a separate thread
    # START THIS IF NEEDED AFTER
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    jsonfuzz_generator_thread = Thread(target=generate_json_fuzzed_output, args=(s, fuzzed_input))
    jsonfuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    jsonfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    binary_checker_thread.join()

