import subprocess
import time
import sys
import threading
import re
import logging

# Load logging configuration
logging.config.fileConfig('logging.conf')

# Now create a logger
logger = logging.getLogger(__name__)


# Counters
total_inputs_processed = 0
bad_outputs_found = 0
non_segmentation_errors = 0

# Locks
total_inputs_lock = threading.Lock()
bad_outputs_lock = threading.Lock()
non_segmentation_errors_lock = threading.Lock()

bad_output_found = False

def run_binary_bytes(binary_path, q, output_q):
    start_time = time.time()
    time_limit = 180  # 180 seconds

    while True:
        global bad_output_found
        global total_inputs_processed  # Declare as global
        global bad_outputs_found       # Declare as global
        global non_segmentation_errors # Declare as global
        if bad_output_found:
            logging.info("Stopping execution because a bad output was found.")
            return
        new_time = time.time()
        if new_time - start_time > time_limit:
            logging.info("Time limit reached, stopping execution.")
            break
        if not q.empty():
            input_data = q.get()['input']
            with total_inputs_lock:
                total_inputs_processed += 1
            logging.info(f"Processing new input. Total inputs processed: {total_inputs_processed}")

            try:
                trace_cmd = f'ltrace {binary_path}'  # Using ltrace
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

                # Decode standard error output to get the trace
                trace_output = process.stderr.decode()
                if "killed by SIGSEGV " in trace_output:
                    with bad_outputs_lock:
                        bad_outputs_found += 1

                    logging.error("Found bad output, writing to bad.txt and stopping execution.")
                    with open('bad.txt', 'wb') as file:
                        file.write(input_data)
                    bad_output_found = True
                    return
                elif "killed by " in trace_output:
                    with non_segmentation_errors_lock:
                        non_segmentation_errors += 1
                    logging.warning("Found a non-segmentation error, writing to bad.txt.")

                # Regular expression to match function calls in ltrace output
                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)

                output_q.put({"input":input_data,"functions":function_calls,"count":len(function_calls)})
            
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
        else:
            time.sleep(5)

def run_binary_string(binary_path, q, output_q):
    start_time = time.time()
    time_limit = 180  # 150 seconds
    while True:
        global bad_output_found
        global total_inputs_processed  # Declare as global
        global bad_outputs_found       # Declare as global
        global non_segmentation_errors # Declare as global
        if bad_output_found:
            logging.info("Stopping execution because a bad output was found.")
            return
        new_time = time.time()
        if new_time - start_time > time_limit:
            logging.info("Time limit reached, stopping execution.")
            return
        if not q.empty():
            input_data = q.get()['input']
            with total_inputs_lock:
                total_inputs_processed += 1
            logging.info(f"Processing new input. Total inputs processed: {total_inputs_processed}")

            try:
                input_bytes = input_data.encode('utf-8')
                trace_cmd = f'ltrace {binary_path}'  # Using ltrace
                process = subprocess.run(trace_cmd, input=input_bytes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

                # Decode standard error output to get the trace
                trace_output = process.stderr.decode()
                if "killed by SIGSEGV" in trace_output:
                    with bad_outputs_lock:
                        bad_outputs_found += 1
                    logging.error("Found bad output, writing to bad.txt and stopping execution.")
                    with open('bad.txt', 'w') as file:
                        file.write(input_data)
                    bad_output_found = True
                    return
                elif "killed by " in trace_output:
                    with non_segmentation_errors_lock:
                        non_segmentation_errors += 1
                    logging.warning("Found a non-segmentation error, writing to bad.txt.")

                # Regular expression to match function calls in ltrace output
                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)

                output_q.put({"input":input_data,"functions":function_calls,"count":len(function_calls)})
            
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
        else:
            time.sleep(5)

def run_strings(binary_path):
    return subprocess.check_output(["/bin/strings", "-s|", "-d", binary_path], stderr=subprocess.PIPE)
