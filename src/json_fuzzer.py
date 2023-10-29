import itertools
import json
from harness import run_binary_and_check_segfault
from library.helpers import get_dict_all_keys, get_dict_all_keys_of_type, update_nested_dict
import random
##########################
## JSON SPECIFIC METHODS ##
##########################

# ADD JSON FUZZ STRATS HERE

def strat1(data: dict):
    """Add new key"""
    data["AAAA"] = "AAAA"
    return data


def strat2(data: dict):
    """Strategy 2: Nesting"""
    max_depth = 50 # CRITICAL: SET MAX DEPTH
    for _ in range(max_depth):
        data = {
            "data": [data]
            }
    return data

def strat3(data: dict):
    """Strategy 3: Long Strings
        find a random string field and edit value to long string
    """
    keys_to_check = get_dict_all_keys_of_type(data, str)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = "A"*10000
    value = data
    for key in key_tup:
        value = value[key]
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value

    update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat4(data: dict):
    """Strategy 4: Numerical Extremes
        def strat4(data: dict):
    """
    keys_to_check = get_dict_all_keys_of_type(data, int)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_values = [1e100, 1e9999, -1, 420.69, 999999999999999999999999, -999999999999, 0]
    updated_value = random.choice(updated_values)
    value = data
    for key in key_tup:
        value = value[key]
    if isinstance(value, list):
        value[random.randint(0, len(value)-1)] = updated_value
        updated_value = value

    data = update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat5(data: dict):
    """Strategy 5: Large Amount of Keys
    def strat5(data: dict):
    """
    for i in range(1000):
        data[f"key{i}"] = f"value{i}"
    return data

# def strat6(data: dict):
#     """Strategy 6: Trailing Comma
#     def strat6(data: dict):
    
#     Trailing commas are not allowed in standard JSON, 
#     tests how JSON parsers handle non-standard input
#     """
#     key = list(data)[-1]

#     if (isinstance(str)): data[key] += ","
#     return data
    


def strat7(data: dict):
    """Strategy 7: send null values
        def strat7(data: dict):
    """
    keys_to_check = get_dict_all_keys(data)
    if not keys_to_check:
        return data
    key_tup = random.choice(keys_to_check)
    updated_value = None
    update_nested_dict(data, list(key_tup), updated_value)
    return data

def strat9(data: dict):
    """Strategy 9: send null-like values
        def strat9(data: dict):
    """
    keys_to_check = get_dict_all_keys(data)
    key_tup = random.choice(keys_to_check)
    value = data
    for key in key_tup:
        value = value[key]
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

    update_nested_dict(data, list(key_tup), updated_value)
    return data


def generate_json_fuzzed_output(df, q):
    json_mutator = [
        strat1,
        strat2,
        strat3,
        strat4,
        strat5,
        strat7,
        strat9,
    ]
    df =  json.loads(df)

    for r in range(1, len(json_mutator) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(json_mutator, r):  # All combinations of size r
            for i in range(10):
                fuzzed_output = df
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                
                json_string = json.dumps(fuzzed_output)

                q.put(json_string)

