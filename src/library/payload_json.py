import json
from typing import Any, Union

from library import Payload
from .helpers import get_dict_all_keys, update_nested_dict, get_nested_dict


class PayloadJson(Payload): 
    def __init__(self, payload: str):
        payload = json.loads(payload)
        super().__init__(payload)
        self.keys = get_dict_all_keys(self.payload)

    def output(self) -> str:
        return json.dumps(self.payload)

    def set_field(self, field: Union[str, tuple[str]], val: Any):
        if isinstance(field, str):
            self.payload[field] = val
            self.keys.append((field,))
        else:
            update_nested_dict(self.payload, list(field), val)
            self.keys.append(field)

    def get_keys(self) -> list[tuple[str]]:
        return self.keys

    def get_val(self, field: Union[str, tuple]) -> Any:
        if isinstance(field, str):
            return self.payload[field]
        return get_nested_dict(self.payload, list(field))

    def get_keys_of_type(self, t: type) -> list[tuple[str]]:
        keys = []
        for k in self.keys:
            v = self.get_val(k)
            if type(v) == t:
                keys.append(k)
        return keys

    def get_data(self) -> dict:
        return self.payload
