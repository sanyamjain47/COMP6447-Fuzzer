"""
###########################
## plaintext SPECIFIC METHODS ##
###########################
"""
import itertools
from random import randint, choice
from re import findall
from copy import copy

def increment_random_number(s: str, _):
    numbers = findall(r'\d+', s)

    if not numbers:
        return s

    random_number = choice(numbers)
    incremented_number = str(int(random_number) + 1)
    return s.replace(random_number, incremented_number, 1)

def decrement_random_number(s: str, _):
    numbers = findall(r'\d+', s)

    if not numbers:
        return s

    random_number = choice(numbers)
    incremented_number = str(int(random_number) - 1)
    return s.replace(random_number, incremented_number, 1)

def increment_random_byte(s: str, _):
    if not s:
        return s

    pos = randint(0, len(s)-1)
    return s[:pos] + chr(ord(s[pos])+1) + s[pos+1:]

def decrement_random_byte(s: str, _):
    if not s:
        return s
    pos = randint(0, len(s)-1)
    return s[:pos] + chr(ord(s[pos])-1) + s[pos+1:]

def bit_flip(s: str, _):
    if not s:
        return s
    pos = randint(0, len(s) - 1)
    char = s[pos]
    bits_to_flip = randint(1, 7)
    for _ in range(bits_to_flip):
        bit = 1 << randint(0, 6)
        char = chr(ord(char) ^ bit)
    return s[:pos] + char + s[pos+1:]

def replace_with_keyword(_, keywords):
    return choice(keywords)

def append_keyword(s: str, keywords):
    return s + choice(keywords)

def null_byte(s: str, _):
    return s + "\x00"

def new_line(s: str, _):
    return s + "\n"

def special_char(s: str, _):
    specials = ["~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", "]", "[", "|", "\\", "`", ",", ".", "/", "?", ";", ":", "'", "<"]
    return s + choice(specials)
    

def f_string(s: str, _):
    return s + "%s%s%s%s%s%s"

def extend(s: str, _):
    return s + "A" * 127

def double_it(s: str, _):
    return s + s

def generate_plain_fuzzed_output(df, q, keywords):
    plain_mutator = [
        decrement_random_byte,
        increment_random_byte,
        decrement_random_number,
        increment_random_number,
        bit_flip,
        replace_with_keyword,
        append_keyword,
        null_byte,
        new_line,
        special_char,
        f_string,
        extend,
        double_it,
    ]

    for r in range(len(plain_mutator)):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(plain_mutator, r):  # All combinations of size r
            for _ in range(10):
                fuzzed_output = copy(df)
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output, keywords)  # Apply each mutator in the combination to the string
                plain_string = str(fuzzed_output)
                q.put(plain_string)
