from pwn import *
from queue import Queue
import sys
import subprocess


def run_binary_and_check_segfault(binary_path, q):
    start_time = time.time()
    time_limit = 150  # 150 seconds
    
    while time.time() - start_time < time_limit:
        if not q.empty():
            input_data = q.get()
            try:
                process = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred with exit code: {e.returncode}")
        else:
            # Sleep for a short duration to avoid busy-waiting
            time.sleep(5)