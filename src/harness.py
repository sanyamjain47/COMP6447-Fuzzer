import subprocess
import time
import sys
import threading

# Shared flag to signal termination
terminate_flag = threading.Event()

def run_binary_bytes(binary_path, q):
    start_time = time.time()
    time_limit = 150  # 150 seconds

    while not terminate_flag.is_set() and time.time() - start_time < time_limit:
        if not q.empty():
            input_data = q.get()['input']
            try:
                trace_cmd = f"ltrace -o trace_output.txt {binary_path}"
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode in [-11, -6]:
                    print(f"An error occurred with exit code: {e.returncode}")
                    terminate_flag.set()
                    sys.exit()
                elif e.returncode < 0 and e.returncode != -2:
                    print(f"Exit code encountered: {e.returncode}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            time.sleep(5)

    print("Exiting run_binary_bytes")


# Ensure that threads check the terminate_flag regularly and terminate if it's set


def run_binary_string(binary_path, q):
    start_time = time.time()
    time_limit = 150  # 150 seconds

    while not terminate_flag.is_set() and time.time() - start_time < time_limit:
        if not q.empty():
            input_data = q.get()['input']
            try:
                input_data = input_data.encode('utf-8')
                process = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode in [-11, -6]:
                    print(f"An error occurred with exit code: {e.returncode}")
                    terminate_flag.set()
                    sys.exit()
                elif e.returncode < 0 and e.returncode != -2:
                    print(f"Exit code encountered: {e.returncode}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            time.sleep(5)
            print(5)

