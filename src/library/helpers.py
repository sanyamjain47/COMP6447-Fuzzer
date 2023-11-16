"""Helper functions"""

from typing import Any

def get_dict_all_keys(data: dict[str, Any]) -> list[tuple[str]]:
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

def get_dict_all_keys_of_type(data: dict[str, Any], t: type) -> list[tuple[str]]:
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
        elif isinstance(v, list):
            if v and isinstance(v[0], t):
                all_keys.append(tuple(k))
                break
        elif isinstance(v, t):
            all_keys.append(tuple(k))
    return all_keys


def update_nested_dict(nested_dict: dict, keys: list, new_value: Any):
   if len(keys) == 1:
      nested_dict[keys[0]] = new_value
   else:
      key = keys[0]
      if key in nested_dict:
         update_nested_dict(nested_dict[key], keys[1:], new_value)


def get_nested_dict(nested_dict: dict[Any, Any], keys: list[str]) ->  Any:
   if len(keys) == 1:
      return nested_dict[keys[0]]
   else:
      key = keys[0]
      if key in nested_dict:
         return get_nested_dict(nested_dict[key], keys[1:])
