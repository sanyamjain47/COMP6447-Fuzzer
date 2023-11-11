import itertools
from queue import Queue
import subprocess
import sys
from harness import run_binary_and_check_segfault
import xml.etree.ElementTree as et
from pwn import *
##########################
## XML SPECIFIC METHODS ##
##########################


'''
1. delete closing tags
2/ delete the > of the tag
2. tags not inside eachother 
3. two roots / more 
4. rogue ampersands?
5. <?xml version="1.0" encoding="UTF-8"?>

XML documents must have a root element
XML elements must have a closing tag
XML tags are case sensitive
XML elements must be properly nested
XML attribute values must be quoted

'''

def rearrange_tags(xml_root):
    #TODO
    return xml_root

def add_root(xml_root):
    #TODO
    return xml_root

def remove_closing_tag(xml_root):
    #TODO: maybe not necessary as basic functions will cover (but more randomly)
    return xml_root

def capitalise_random_tag(xml_root):
    # TODO: maybe not necessary as basics could cover this
    return xml_root

def add_symbols(xml_root):
    # TODO: insert &">?"    against maybe not necessary
    return xml_root

def remove_quotations(xml_root):
    #TODO remove "for vakue attributes"
    return xml_root

def modify_nesting(xml_root):
    #TODO 
    return xml_root

def header(xml_root):
    # TODO insert / move header   <?xml version="1.0" encoding="UTF-8"?>
    return xml_root


def fuzz_xml(xml, queue):
    xml_mutators = [
        rearrange_tags,
        add_root,
        remove_closing_tag,
        capitalise_random_tag,
        add_symbols,
        remove_quotations,
        modify_nesting,
        header
    ]

    for r in range(1, len(xml_mutators) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(xml_mutators, r):  # All combinations of size r
                fuzzed_output = xml
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                queue.put(fuzzed_output)



# def format_xml(file_path: str):
#     data = []
#     tree = et.parse(file_path)
#     root = tree.getroot()
#     for children in root:
#         for sub_elements in children:
#             data.append(sub_elements)

#     return data
                

# TODO: deleteing//// for Testing
def run_binary(binary_path: str, q: Queue):

    input_data = q.get()

    p = process(binary_path)
    p.sendline(input_data.encode())
    #print(p.recvall())

    try:
        p = subprocess.run([binary_path], input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode == -11:
            print(f"An error occurred with exit code: {e.returncode}")
            print(f"The input the caused the error has been put in bad.txt")
            sys.exit()
    print("No errors found")



if __name__ == "__main__":
    q = Queue()
    with open('test_inputs/xml.txt', 'r') as f:
        content = f.read()
        print(content)

    q.put(content)
    run_binary("../assignment/xml1", q)

