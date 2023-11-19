"""
###########################
## JSON SPECIFIC METHODS ##
###########################
"""
import itertools

from copy import deepcopy

from library import PayloadJson
import random


def keywords(data: PayloadJson, keywords):
    """Strategy 0: keyword Strings
        find a random string field and edit value to keyword string
    """
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = random.choice(keywords)
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def more_keys(data: PayloadJson, _):
    """Add new key"""
    data.set_field("AAAA", "AAAA")
    return data


def nesting(data: PayloadJson, _):
    """Strategy 2: Nesting"""
    max_depth = 5 # CRITICAL: SET MAX DEPTH
    for i in range(max_depth):
        data.set_field(f"data{i}", [deepcopy(data.get_data())], update_keys=False)
    return data


def long_strings(data: PayloadJson, _):
    """Strategy 3: Long Strings
        find a random string field and edit value to long string
    """
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = "A"*10000
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def magic_numbers(data: PayloadJson, _):
    """Strategy 4: Numerical Extremes
        def strat4(data: dict, _):
    """
    keys_to_check = data.get_keys_of_type(int)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_values = [1e100, 1e9999, -1, 420.69, 999999999999999999999999, -999999999999, 0]
    updated_value = random.choice(updated_values)
    value = data.get_val(key_tup)
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value
    data.set_field(key_tup, updated_value)
    return data

def large_keys(data: PayloadJson, _):
    """Strategy 5: Large Amount of Keys
    def strat5(data: dict, _):
    """
    for i in range(1000):
        data.set_field(f"key{i}", f"value{i}", update_keys=False)
    return data

# def strat6(data: dict, _):
#     """Strategy 6: Trailing Comma
#     def strat6(data: dict, _):
    
#     Trailing commas are not allowed in standard JSON, 
#     tests how JSON parsers handle non-standard input
#     """
#     key = list(data)[-1]

#     if (isinstance(str)): data[key] += ","
#     return data
    


def null_values(data: PayloadJson, _):
    """Strategy 7: send null values
        def strat7(data: dict, _):
    """
    keys_to_check = data.get_keys()
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, None)
    return data

def null_like_values(data: PayloadJson, _):
    """Strategy 9: send null-like values
        def strat9(data: dict, _):
    """
    keys_to_check = data.get_keys()
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    value = data.get_val(key_tup)
    if isinstance(value, list):
        updated_value = []
    elif isinstance(value, str):
        updated_value = ""
    elif isinstance(value, int):
        updated_value = 0
    elif isinstance(value, dict):
        updated_value = {}
    elif isinstance(value, float):
        updated_value = 0.0
    else:
        updated_value = None
    data.set_field(key_tup, updated_value)
    return data

def fstrings(data: PayloadJson, _):
    keys_to_check = data.get_keys_of_type(str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    data.set_field(key_tup, "%s%s%s%s")
    


def generate_json_fuzzed_output(df, q, keywords):
    json_mutator = [
        keywords,
        more_keys,
        nesting,
        long_strings,
        magic_numbers,
        large_keys,
        null_values,
        null_like_values,
        fstrings,
    ]

    for r in range(len(json_mutator)):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(json_mutator, r):  # All combinations of size r
            for _ in range(10):
                fuzzed_output = PayloadJson(df)
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output, keywords)  # Apply each mutator in the combination to the string
                json_string = str(fuzzed_output)
                q.put(json_string)
