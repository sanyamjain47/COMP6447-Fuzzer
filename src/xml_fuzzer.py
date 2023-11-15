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


# et is the object istnce of the tree

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

def rearrange_tags(f: str):
    data = []
    #root = et.fromstring(xml)
    
    print("lines are")
    for line in f:
        data.append(line)
        #print(line, end="") 
    

    # for elem in root.findall(".//"):
    #     elem.text = "NEW TEXT!"   
    #     elem.set("SET","NUMBER\"")
    #     data.append(elem)
        

    # print(et.dump(root))
    # for elem in root.findall(".//"):
    #     print(elem.tag)
    #     data.append(elem)

    # for child in root:
    #     for sub_elem in child:
    #         sub_elem.text = "NEWW TEXT?????"
    # print(et.dump(root))


    #print("length data = {}".format(len(data)))

    index1 = random.randrange(len(data)) # len data - 1?
    index2 = random.randrange(len(data))

    # swapping tag1 and tag2 position
    tag1 = data[index1] # tag1
    data[index1] = data[index2]
    data[index2] = tag1

    print("Swapping {} and {} to get:".format(data[index1], data[index2]))
    
    
    
    xml_str = array_to_str(data)
    print(xml_str)
    return xml_str 


def array_to_str(lst):
    xml = ""
    for row in lst:
        xml += row
    return xml

# def format_xml(file_path: str):
#     data = []
#     tree = et.parse(file_path)
#     root = tree.getroot()
#     for children in root:
#         for sub_elements in children:
#             data.append(sub_elements)

#     return data


# XML files are only valid if there is one root 
# returns a new xml str with 2 roots (same tag)
def add_root(f: str):
    xml = f.read
    root = et.fromstring(xml)
    new_root = "<{}>\n<\\{}>".format(root.tag, root.tag)
    print(xml + new_root)
    return xml + new_root

def remove_closing_tag(f: str):

    #TODO: maybe not necessary as basic functions will cover (but more randomly)
    return xml



def capitalise_random_tag(f: str):
    # TODO: maybe not necessary as basics could cover this
    return xml_root

def add_symbols(f: str):
    # TODO: maybe edit so it puts the symbol somewhere more specific
    symbols = ['<', '>', '<\\', '<>', '&', '^', '=', '\'', '\"']
    symbol = random.choice(symbols)
    pos = random.randint(0, len(xml))
    print("Inserting symbol '{}'".format(symbol), "at position {} to get: \n".format(pos), xml[:pos] + symbol + xml[pos:])
    return xml[:pos] + symbol + xml[pos:]


def remove_quotations(f: str):
    # loop through
    # if char = "" then remove some randomly
    #TODO remove "for vakue attributes"
    return xml_root

def modify_nesting(f: str):
    # can do this with et.indent()
    #TODO 
    return xml_root

def header(f: str):
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
        content = f.read # pass input on as the file and convert it to content
        #root = et.fromstring(content)
        fuzzed_input = rearrange_tags(f)

    q.put(fuzzed_input)
    run_binary("../assignment/xml1", q)

