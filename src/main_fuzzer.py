from threading import Thread
from queue import Queue
from base_fuzzer import generate_base_fuzzed_output
from csv_fuzzer import generate_csv_fuzzed_output
from json_fuzzer import generate_json_fuzzed_output
from xml_fuzzer import generate_xml_fuzzed_output
from jpeg_fuzzer import generate_jpeg_fuzzed_output
from plaintext_fuzzer import generate_plain_fuzzed_output
from library import ThreadOutput
from harness import run_strings


# Corpus contains all the fuzzed inputs which give new code coverage
# corpus = []
# ltrace output of code 


def start_csv(s: str, binary_path: str):
    fuzzed_input = Queue()
    fuzzed_output = Queue()

    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    fuzz_generator_thread.start()

    csvfuzz_generator_thread = Thread(target=generate_csv_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    csvfuzz_generator_thread.start()


    # Wait for both threads to finish
    csvfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    
def start_jpeg(s: bytes, binary_path: str):
    fuzzed_input = Queue()
    fuzzed_output = Queue()

    # fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    # fuzz_generator_thread.start()
    input_data = bytearray(s)
    jpgfuzz_generator_thread = Thread(target=generate_jpeg_fuzzed_output, args=(input_data, fuzzed_input,binary_path, fuzzed_output))
    jpgfuzz_generator_thread.start()


    # Wait for both threads to finish
    jpgfuzz_generator_thread.join()
    # fuzz_generator_thread.join()

def start_json(s: str, binary_path: str):
    fuzzed_input = Queue()
    fuzzed_output = Queue()

    keywords = ThreadOutput(target=run_strings, args=(binary_path,))
    keywords.start()
    k = keywords.join().decode().split("|")

    generate_json_fuzzed_output(s, fuzzed_input,binary_path,fuzzed_output, k)


def start_xml(s:str, binary_path: str):
    fuzzed_input = Queue()
    fuzzed_output = Queue()

    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    fuzz_generator_thread.start()

    xmlfuzz_generator_thread = Thread(target=generate_xml_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    xmlfuzz_generator_thread.start()


    # Wait for both threads to finish
    xmlfuzz_generator_thread.join()
    fuzz_generator_thread.join()


def start_txt(s:str, binary_path: str):

    fuzzed_input = Queue()
    fuzzed_output = Queue()
    keywords = ThreadOutput(target=run_strings, args=(binary_path,))
    keywords.start()

    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output))
    fuzz_generator_thread.start()
    k = keywords.join().decode().split("|")

    txtfuzz_generator_thread = Thread(target=generate_plain_fuzzed_output, args=(s, fuzzed_input,binary_path, fuzzed_output, k))
    txtfuzz_generator_thread.start()


    # Wait for both threads to finish
    txtfuzz_generator_thread.join()
    fuzz_generator_thread.join()


# Generic fuzzer for inputs that have not been implemented yet
def start_general(s: str, binary_path: str):
    fuzzed_input = Queue()

    # Start generating inputs in a separate thread
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    # Run this function in another thread concurrently
    # binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    # binary_checker_thread.start()

    # Wait for both threads to finish
    fuzz_generator_thread.join()
    # binary_checker_thread.join()
