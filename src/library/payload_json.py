"""Payload class for json"""
import json
from typing import Any, Union

from library import Payload
from .helpers import get_dict_all_keys, update_nested_dict, get_nested_dict


class PayloadJson(Payload):
    """Payload class for json will take in input of a string and allow for modifications"""
    def __init__(self, payload: str):
        payload = json.loads(payload)
        self.trailing_comma: bool = False
        self.extras: list = []
        super().__init__(payload)
        self.keys = get_dict_all_keys(self.payload)

    def __str__(self) -> str:
        """Produce Json output"""
        return json.dumps(self.payload)
    

    def set_field(self, field: Union[str, tuple[str]], val: Any, update_keys: bool = True):
        """set field in json obj"""
        if isinstance(field, str):
            self.payload[field] = val
            if (update_keys):
                self.keys.append((field,))
        else:
            update_nested_dict(self.payload, list(field), val)
            if (update_keys):
                self.keys.append(field)


    def get_keys(self) -> list[tuple[str]]:
        """set get list of tuples of keys to access object and nested objs"""
        return self.keys

    def get_val(self, field: Union[str, tuple]) -> Any:
        """return the value at a key or nested key"""
        if isinstance(field, str):
            return self.payload[field]
        return get_nested_dict(self.payload, list(field))

    def get_keys_of_type(self, t: type) -> list[tuple[str]]:
        """get all keys corresponding to types"""
        keys = []
        for k in self.keys:
            v = self.get_val(k)
            if isinstance(v, t):
                keys.append(k)
        return keys

    def add_extra_val(self, key: str, val: Any):
        self.extras += (key, val)

    def set_trailing_comma(self, val: bool):
        self.trailing_comma = val

    def get_data(self) -> dict:
        """get the raw dictionary data"""
        return self.payload
