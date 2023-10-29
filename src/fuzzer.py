import random
from pwn import *
#TODO: actually run the fuzzer on the inout (implement these functions into the main code)

# The fuzzing functions below (should) fuzz despite what format the textfile is
# Each function takes in input as a string and performs bite/bytes operations and returns the string. 
# The string (text file) can then be run against the program


# Randomly selects a mutator to run on the given input
def fuzzer(s: str) -> str:
    mutators = [
        delete_random_byte,
        insert_random_byte,
        bit_flip, 
        append_random_num_bytes, # might be useless (test for usless mutations and get rid of them)
        append_random_num_str
    ]

    mutator = random.choice(mutators)
    print(mutator)
    return mutator(s)


# Flips one bit of a character in a string
def bit_flip(s: str):
    if s == "":
        return s
    
    print(s)
    pos = random.randint(0, len(s) - 1)
    char = s[pos]
    bit = 1 << random.randint(0, 6) # select one bit to flip 
    new_char = chr(ord(char) ^ bit)
    print("Bit flipped:", bit, "Old character:", repr(char) + ", New character:", repr(new_char))

    print(s[:pos] + new_char + s[pos+1:])
    return s[:pos] + new_char + s[pos+1:]


# Deletes a random character from the string
def delete_random_byte(s: str):
    print(s)
    if s == "":
        return s
    
    pos = random.randint(0, len(s) - 1)
    print("Deleted character:", s[pos])
    return s[:pos] + s[pos+1:]

def insert_random_byte(s: str):
    print("TODO")
    return s

# Adds a random number of characters to the end of the text files
def append_random_num_bytes(s: str):
    print(s)
    if s == "":
        return s
    
    num_bytes = random.randint(1, 1000)
    random_char = chr(random.randrange(32,127))
    print("appending", num_bytes, "x", random_char, "to string")
    return s + (num_bytes*random_char) 

# To the end of the input, appends a substring, x number of times
# this breaks csv1 after a number of runs
def append_random_num_str(s: str):
    print(s)
    if s == "":
        return s
    lower_bound = random.randint(0, len(s)-2)
    upper_bound = random.randint(lower_bound, len(s)-1)
    multiplier = random.randint(1, 200)
    return s + (s[lower_bound: upper_bound] * multiplier)







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


        
