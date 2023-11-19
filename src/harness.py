import subprocess
import time
import sys
import threading
import re
# Shared flag to signal termination
terminate_flag = threading.Event()

def run_binary_bytes(binary_path, q, output_q):
    start_time = time.time()
    time_limit = 150  # 150 seconds

    while time.time() - start_time < time_limit:
        if not q.empty():
            input_data = q.get()['input']
            try:
                trace_cmd = f"ltrace {binary_path}"
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                print("Standard Output:", process.stdout.decode())
                print("Standard Error:", process.stderr.decode())
            except subprocess.CalledProcessError as e:
                print("Standard Output:", e.stdout.decode())
                print("Standard Error:", e.stderr.decode())
                if e.returncode in [-11, -6]:
                    print(f"An error occurred with exit code: {e.returncode}")
                    sys.exit()
                elif e.returncode < 0 and e.returncode != -2:
                    print(f"Exit code encountered: {e.returncode}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            time.sleep(5)

    print("Exiting run_binary_bytes")

# Ensure that threads check the terminate_flag regularly and terminate if it's set

def run_binary_string(binary_path, q,output_q):
    start_time = time.time()
    time_limit = 180  # 150 seconds

    while True:
        if time.time() - start_time > time_limit:
            break
        if not q.empty():
            input_data = q.get()['input']
            try:
                input_bytes = input_data.encode('utf-8')
                trace_cmd = f'ltrace {binary_path}'  # Using ltrace
                process = subprocess.run(trace_cmd, input=input_bytes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

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