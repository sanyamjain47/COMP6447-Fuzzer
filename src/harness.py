import subprocess
import time
import sys
import threading
import re

def run_binary_bytes(binary_path, q, output_q):
    start_time = time.time()
    time_limit = 180  # 150 seconds

    while True:
        new_time = time.time()
        if new_time - start_time > time_limit:
            break
        if not q.empty():
            input_data = q.get()['input']
            try:
                trace_cmd = f'ltrace {binary_path}'  # Using ltrace
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

                # Decode standard error output to get the trace
                trace_output = process.stderr.decode()
                if "killed by" in trace_output:
                    print("FOUND ITTT")
                    sys.exit()
                # Regular expression to match function calls in ltrace output
                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)

                output_q.put({"input":input_data,"functions":function_calls,"count":len(function_calls)})
            
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            time.sleep(5)
    print("exiting harness")

# Ensure that threads check the terminate_flag regularly and terminate if it's set

def run_binary_string(binary_path, q,output_q):
    start_time = time.time()
    time_limit = 180  # 150 seconds
    print("Starting harness")
    while True:
        new_time = time.time()
        if new_time - start_time > time_limit:
            return
        if not q.empty():
            input_data = q.get()['input']
            try:
                input_bytes = input_data.encode('utf-8')
                trace_cmd = f'ltrace {binary_path}'  # Using ltrace
                process = subprocess.run(trace_cmd, input=input_bytes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,timeout=5)

                # Decode standard error output to get the trace
                trace_output = process.stderr.decode()
                if "killed by" in trace_output:
                    print("FOUND ITTT")
                    sys.exit()
                # Regular expression to match function calls in ltrace output
                func_call_pattern = re.compile(r'(\w+)\(')
                function_calls = func_call_pattern.findall(trace_output)

                output_q.put({"input":input_data,"functions":function_calls,"count":len(function_calls)})
            
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            time.sleep(10)
