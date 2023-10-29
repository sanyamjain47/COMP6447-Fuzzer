from pwn import *

# Run this multithreaded
def run_binary_and_check_segfault(binary_path, input_data):
    try:
        process = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        
        return False
        
    except subprocess.CalledProcessError as e:
        print("An error occurred with exit code:", e.returncode)
        return True
