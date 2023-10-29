import sys
import json
from pwn import *
import file_type


def run_program(path: str, payload: str):
    p = process(path)
    # payload = payload + "\n"
    payload = "AAAAA,AAAAAAA.AAAAAAAAA,AAAAAA,AAAAAAAAA"
    p.sendline(payload.encode())
    print(p.recvall())

    # detect whether error of interest, e.g. SIGSEV, 
    error = 1 # for now 
    if (error):
        with open("./bad.txt", "wb+") as f: # OR p.log_file()
            f.write(f"ERROR --> input: {payload}".encode())

    p.close()


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

    payload = file_type.read_and_determine_data(temp_path)
    print(payload)
    if isinstance(payload, dict):
        payload = json.dumps(payload)


    print("Fuzzing this thing...")
    counter = 0
    while counter < 1:
        run_program(bin_path, payload)
        counter += 1

    if (os.stat("bad.txt").st_size != 0): print("Found bad input.")
        
