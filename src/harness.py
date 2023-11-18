from pwn import *
from queue import Queue
import sys
import subprocess


def run_binary_and_check_segfault(binary_path, q: Queue):
    start_time = time.time()
    time_limit = 150  # 150 seconds
    
    while time.time() - start_time < time_limit:
        if not q.empty():
            input_data = q.get()
            try:
                process = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            except subprocess.CalledProcessError as e:
                if e.returncode == -11:
                    print(f"An error occurred with exit code: {e.returncode}")
                    generate_report(input_data,e)
                    print(f"The input the caused the error has been put in bad.txt")
                    sys.exit()
                if e.returncode == -6:
                    print(f"An error occurred with exit code: {e.returncode}")
                    generate_report(input_data,e)
                    print(f"The input the caused the error has been put in bad.txt")
                    sys.exit()

        else:
            # Sleep for a short duration to avoid busy-waiting
            time.sleep(5)

def run_strings(binary_path):
    return subprocess.check_output(["/bin/strings", "-s|", "-d", binary_path], stderr=subprocess.PIPE)
        
def generate_report(s: str, e):
    with open('bad.txt', 'a') as f:
        f.write("Input causing the error:\n{}\n".format(s))
        f.write("Error code: {}\n".format(e.returncode))
        f.write("=" * 40 + "\n")  # Add a separator for readability

