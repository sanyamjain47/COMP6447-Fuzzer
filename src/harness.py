from pwn import *
from queue import Queue
import sys
# Run this multithreaded
import subprocess

def run_binary_and_check_segfault(binary_path, q):
    while not q.empty():
        input_data = q.get()
        try:
            process = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred with exit code: {e.returncode}")
