import sys
import json
from pwn import *
from enum import Enum


class TemplateTypes(Enum):
    CSV = "csv"
    JSON = "json"

def run_program(path: str, payload: str):
    p = process(path)
    p.sendline(payload.encode())
    print(p.recvall())
    p.close()


if __name__ == "__main__":
    
    # print(sys.argv)
    if (len(sys.argv) != 4):
        print(f"Usage: python3 {sys.argv[0]} <Binary Path> <Template Path> <Type>")
        exit()

    bin_path = sys.argv[1]
    temp_path = sys.argv[2]
    bin_type = sys.argv[3]
    payload = ""

    with open(temp_path, "r") as f:
        if (bin_type == TemplateTypes.CSV.value):
            rows = f.read().split("\n")
            header = rows[0]
            print(header)
            payload = header + f"\n {','.join(['A' for _ in range(len(header))])}\n\n"
        elif (bin_type == TemplateTypes.JSON.value):
            data = json.load(f)
            payload = {k: "A" for k in data.keys()}

    run_program(bin_path, payload)

        
