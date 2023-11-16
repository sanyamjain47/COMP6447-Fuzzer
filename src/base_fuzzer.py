import random
import itertools
from queue import Queue
from pwn import log

###################
## BASIC METHODS ##
###################

# Flips one bit of a character in a string
def bit_flip(s: str):
    if not s:
        return s
    
    pos = random.randint(0, len(s) - 1)
    char = s[pos]
    bits_to_flip = random.randint(1, 7)
    for _ in range(bits_to_flip):
        bit = 1 << random.randint(0, 6)
        char = chr(ord(char) ^ bit)
    return s[:pos] + char + s[pos+1:]



# Deletes a random character from the string
def delete_random_byte(s: str):
    if not s:
        return s
    
    pos = random.randint(0, len(s) - 1)
    length = random.randint(1, len(s) - pos)
    return s[:pos] + s[pos+length:]


def insert_random_byte(s: str):
    pos = random.randint(0, len(s))
    length = random.randint(1, 10)
    random_bytes = ''.join(chr(random.randrange(32,127)) for _ in range(length))
    return s[:pos] + random_bytes + s[pos:]


# Adds a random number of characters to the end of the text files
def append_random_num_bytes(s: str):
    if not s:
        return s
    
    num_bytes = random.randint(1, 50)
    random_char = chr(random.randrange(32,127))
    return s + (num_bytes * random_char)


# To the end of the input, appends a substring, x number of times
# this breaks csv1 after a number of runs
def append_random_num_str(s: str):
    if not s:
        return s
    
    lower_bound = random.randint(0, len(s) - 1)
    upper_bound = random.randint(lower_bound, len(s))
    multiplier = random.randint(1, 10)
    return s + (s[lower_bound: upper_bound] * multiplier)




def generate_base_fuzzed_output(s: str, q):
    base_mutators = [
        delete_random_byte,
        insert_random_byte,
        bit_flip,
        append_random_num_bytes,
        append_random_num_str
    ]
    all_mets = set()
    q.put(s)
    for r in range(1, len(base_mutators) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(base_mutators, r):  # All combinations of size r
            #log.info("mutator_combination = {}".format(mutator_combination))
            for i in range(5): # 10 is a constant to run every type of combination atleast 10 times. Can be reduced
                fuzzed_output = s
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                    # print(fuzzed_output)
                    # log.info("Currently mutatating using: {}".format(mutator))
                q.put(fuzzed_output)
                all_mets.add(mutator_combination)
    #print(all_mets)
    log.info('all combinations done???')
    #generate_base_fuzzed_output(s,q)

# Test it out
if __name__ == "__main__":
    generate_base_fuzzed_output("test_string")
