from threading import Thread
from queue import Queue
from base_fuzzer import generate_base_fuzzed_output
from harness import run_binary_and_check_segfault, run_strings
from csv_fuzzer import generate_csv_fuzzed_output
from json_fuzzer import generate_json_fuzzed_output
from plaintext_fuzzer import generate_plain_fuzzed_output
from xml_fuzzer import fuzz_xml
from library import ThreadOutput

# Corpus contains all the fuzzed inputs which give new code coverage
# corpus = []
# ltrace output of code 


def start_csv(s: str, binary_path: str):
    fuzzed_input = Queue()

    # Add the first given input to the corpus
    #corpus.append(s)

    ##while True: 
        # Begin running threads
        # Use for loop to continually 
        # run generic thead and retun stuff to cue: 
        # if input gives new branch code add that to dict and run fuzzer on both

        #exit()

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
    binary_checker_thread.join() # TODO FIX ISSUE WITH HANGING THREAD!
    


def start_json(s: str, binary_path: str):
    fuzzed_input = Queue()
    keywords = ThreadOutput(target=run_strings, args=(binary_path,))
    keywords.start()

    # Start generating inputs in a separate thread
    # START THIS IF NEEDED AFTER
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    k = keywords.join().decode().split("|")
    jsonfuzz_generator_thread = Thread(target=generate_json_fuzzed_output, args=(s, fuzzed_input, k))
    jsonfuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    jsonfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    binary_checker_thread.join()

def start_plain(s: str, binary_path: str):
    fuzzed_input = Queue()
    keywords = ThreadOutput(target=run_strings, args=(binary_path,))
    keywords.start()

    # Start generating inputs in a separate thread
    # START THIS IF NEEDED AFTER
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    k = keywords.join().decode().split("|")
    plainfuzz_generator_thread = Thread(target=generate_plain_fuzzed_output, args=(s, fuzzed_input, k))
    plainfuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    plainfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    binary_checker_thread.join()


def start_xml(s:str, binary_path: str):

    fuzzed_input = Queue()

    # Start generating inputs in a separate thread
    xmlfuzz_generator_thread = Thread(target=fuzz_xml, args=(s, fuzzed_input))
    xmlfuzz_generator_thread.start()

    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    xmlfuzz_generator_thread.join()
    fuzz_generator_thread.join()
    binary_checker_thread.join()




# Generic fuzzer for inputs that have not been implemented yet
def start_general(s: str, binary_path: str):
    fuzzed_input = Queue()

    # Start generating inputs in a separate thread
    fuzz_generator_thread = Thread(target=generate_base_fuzzed_output, args=(s, fuzzed_input))
    fuzz_generator_thread.start()

    # Run this function in another thread concurrently
    binary_checker_thread = Thread(target=run_binary_and_check_segfault, args=(binary_path, fuzzed_input))
    binary_checker_thread.start()

    # Wait for both threads to finish
    fuzz_generator_thread.join()
    binary_checker_thread.join()
