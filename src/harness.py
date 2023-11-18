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
                trace_cmd = f"ltrace {binary_path}"
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                print("Standard Output:", process.stdout.decode())
                print("Standard Error:", process.stderr.decode())
            except subprocess.CalledProcessError as e:
                print("Standard Output:", e.stdout.decode())
                print("Standard Error:", e.stderr.decode())
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
                # Convert the string input_data to bytes
                input_data = input_data.encode('utf-8')
                # Prefix the binary path with ltrace
                trace_cmd = f'strace {binary_path}'
                # Run the command with ltrace
                process = subprocess.run(trace_cmd, input=input_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                # Print the standard output and standard error
                print("Standard Output:", process.stdout.decode())
                print("Standard Error:", process.stderr.decode())
            except subprocess.CalledProcessError as e:
                print("Standard Output:", e.stdout.decode())
                print("Standard Error:", e.stderr.decode())
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