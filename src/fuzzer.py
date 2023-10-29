import random
from pwn import *
#TODO: actually run the fuzzer on the inout (implement these functions into the main code)

# The fuzzing functions below (should) fuzz despite what format the textfile is
# Each function takes in input as a string and performs bite/bytes operations and returns the string. 
# The string (text file) can then be run against the program





# When writing these fuzzing functions, I used this main function: (if you want to test it, go to my other branch HARNESS)
'''
class TemplateTypes(Enum):
    CSV = "csv"
    JSON = "json"

def run_program(path: str, payload: str):
    p = process(path)
    p.sendline(payload.encode())
    print(p.recvall())
    p.close()






if __name__ == "__main__":
    
    if (len(sys.argv) != 4):
        print(f"Usage: python3 {sys.argv[0]} <Binary Path> <Template Path>")
        exit()

    bin_path = sys.argv[1]
    temp_path = sys.argv[2]
    bin_type = sys.argv[3]
    payload = ""

    with open(temp_path, "r", encoding='utf-8-sig') as f:
        if (bin_type == TemplateTypes.CSV.value):
            csvr = f.read()
            payload = fuzzer(csvr)
            print(payload)
    
    run_program(bin_path, payload)
'''


        
