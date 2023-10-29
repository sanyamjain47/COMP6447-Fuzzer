import sys
from pwn import *
import file_type
from main_fuzzer import start_csv,start_json

if __name__ == "__main__":
    
    # print(sys.argv)
    if (len(sys.argv) != 3):
        print(f"Usage: python3 main,.py <Binary Path> <Template Path>")
        exit()

    bin_path = sys.argv[1]
    temp_path = sys.argv[2]
    if not file_type.check_file(bin_path,'x') or not file_type.check_file(temp_path,'r'):
        exit()
    
    payload = ""

    payload,type_file = file_type.read_and_determine_data(temp_path)
    # print(payload)
    if type_file == 'CSV':
        start_csv(payload, bin_path)
    elif type_file == 'JSON':
        start_json(payload,bin_path)


