"""Helper functions"""

from functools import lru_cache

def get_dict_all_keys(data: dict) -> list[tuple[str]]:
    """Gets all the keys for a dictionary
    Args:
        d: the dictionary
    Returns
        A list of tuples containing the recustive locations of the keys
    """
    all_keys = list() 
    for k, v in data.items():
        if isinstance(v, dict):
            all_keys += [(k, *keys) for keys in get_dict_all_keys(v)]
        else:
            all_keys.append((k,))
    return all_keys


def get_dict_all_keys_of_type(data: dict, t: type):
    """Gets all the keys for a dictionary
    Args:
        d: the dictionary
    Returns
        A list of tuples containing the recustive locations of the keys
    """
    all_keys = list() 
    for k, v in data.items():
        if isinstance(v, dict):
            all_keys += [(k, *keys) for keys in get_dict_all_keys_of_type(v, t)]
        elif isinstance(v, t):
            all_keys.append((k,))
        elif isinstance(v, list):
            for val in v:
                if isinstance(val, t):
                    all_keys.append((k,))
                    break
    return all_keys


def update_nested_dict(nested_dict: dict, keys: list, new_value: any) -> dict:
   if len(keys) == 1:
      nested_dict[keys[0]] = new_value
   else:
      key = keys[0]
      if key in nested_dict:
         update_nested_dict(nested_dict[key], keys[1:], new_value)
