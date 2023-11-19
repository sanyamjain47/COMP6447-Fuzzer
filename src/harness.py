import subprocess
import time
import sys
import threading
import re
import logging
import logging.config

# Assuming 'logging.conf' is correctly set up in the same directory
logging.config.fileConfig('src/logging.conf')
logger = logging.getLogger(__name__)

# Global counters
total_inputs_processed = 0
bad_outputs_found = 0
non_segmentation_errors = 0

# Locks for thread-safe operations on counters
total_inputs_lock = threading.Lock()
bad_outputs_lock = threading.Lock()
non_segmentation_errors_lock = threading.Lock()

# Flag to indicate discovery of bad output
bad_output_found = False

def run_binary_bytes(binary_path, q, output_q):
    global bad_output_found, total_inputs_processed, bad_outputs_found, non_segmentation_errors
    start_time = time.time()
    time_limit = 180  # 180 seconds

    while True:
        if bad_output_found:
            logger.info("Stopping execution because a bad output was found.")
            return
        if time.time() - start_time > time_limit:
            logger.info("Time limit reached, stopping execution.")
            break
        if not q.empty():
            input_data = q.get()['input']
            with total_inputs_lock:
                total_inputs_processed += 1
            logger.info(f"Processing new input. Total inputs processed: {total_inputs_processed}")

            try:
                process = subprocess.run(
                    ['ltrace', binary_path],
                    input=input_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )

                trace_output = process.stderr.decode()
                if "killed by SIGSEGV " in trace_output:
                    with bad_outputs_lock:
                        bad_outputs_found += 1
                    logger.error("Found bad output, writing to bad.txt and stopping execution.")
                    with open('bad.txt', 'wb') as file:
                        file.write(input_data)
                    bad_output_found = True
                    return
                elif "killed by " in trace_output:
                    with non_segmentation_errors_lock:
                        non_segmentation_errors += 1
                    logger.warning("Found a non-segmentation error, writing to bad.txt.")

                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)
                output_q.put({"input":input_data, "functions":function_calls, "count":len(function_calls)})
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            time.sleep(5)

def run_binary_string(binary_path, q, output_q):
    global bad_output_found, total_inputs_processed, bad_outputs_found, non_segmentation_errors
    start_time = time.time()
    time_limit = 180  # 180 seconds

    while True:
        if bad_output_found:
            logger.info("Stopping execution because a bad output was found.")
            return
        if time.time() - start_time > time_limit:
            logger.info("Time limit reached, stopping execution.")
            return
        if not q.empty():
            input_data = q.get()['input']
            with total_inputs_lock:
                total_inputs_processed += 1
            logger.info(f"Processing new input. Total inputs processed: {total_inputs_processed}")

            try:
                input_bytes = input_data.encode('utf-8')
                process = subprocess.run(
                    ['ltrace', binary_path],
                    input=input_bytes,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )

                trace_output = process.stderr.decode()
                if "killed by SIGSEGV" in trace_output:
                    with bad_outputs_lock:
                        bad_outputs_found += 1
                    logger.error("Found bad output, writing to bad.txt and stopping execution.")
                    with open('bad.txt', 'w') as file:
                        file.write(input_data)
                    bad_output_found = True
                    return
                elif "killed by " in trace_output:
                    with non_segmentation_errors_lock:
                        non_segmentation_errors += 1
                    logger.warning("Found a non-segmentation error, writing to bad.txt.")

                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)
                output_q.put({"input":input_data, "functions":function_calls, "count":len(function_calls)})
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
        else:
            time.sleep(5)

def run_strings(binary_path):
    return subprocess.check_output(["/bin/strings", "-s|", "-d", binary_path], stderr=subprocess.PIPE)
