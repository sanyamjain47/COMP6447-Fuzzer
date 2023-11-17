import itertools
from queue import Queue
import random
import subprocess
import sys
import xml.etree.ElementTree as et
from pwn import *
##########################
## XML SPECIFIC METHODS ##
#########################

def rearrange_tags(xml: str):
    data = xml.splitlines()

    index1 = random.randrange(len(data)) # len data - 1?
    index2 = random.randrange(len(data))

    # swapping tag1 and tag2 position
    tag1 = data[index1]
    data[index1] = data[index2]
    data[index2] = tag1

    # print("Swapping {} and {} to get:".format(data[index1], data[index2]))
    xml_str = lst_to_str(data)
    return xml_str 

# XML files are only valid if there is one root 
# returns a new xml str with 2 roots (same tag)
def add_root(xml: str):
    root = et.fromstring(xml)
    new_root = "<{}>\n<\\{}>".format(root.tag, root.tag)
    return xml + new_root

def remove_key_symbols(xml: str):
    symbols = ['>', '=', '\'', '\"', '?']

    pos_tags = []
    i = 0
    for char in xml:
        if (char in symbols):
            pos_tags.append(i)
        i += 1

    pos = random.choice(pos_tags)
    # print('pos = ', pos)
    # print(xml[:pos] + xml[pos+1:])
    # print("removed byte ", repr(xml[pos]))
    return xml[:pos] + xml[pos+1:]

# Returns the xml with various char capitalised
def capitalise_random(xml: str):
    return ''.join(random.choice((str.upper, str.lower))(char) for char in xml)

def add_symbols(xml: str):
    # TODO: maybe edit so it puts the symbol somewhere more specific
    symbols = ['<', '>', '<\\', '<>', '&', '^', '=', '\'', '\"']
    symbol = random.choice(symbols)
    pos = random.randint(0, len(xml))
    # print("Inserting symbol '{}'".format(symbol), "at position {} to get: \n".format(pos), xml[:pos] + symbol + xml[pos:])
    return xml[:pos] + symbol + xml[pos:]

def modify_nesting(xml: str):
    # can do this with et.indent()?
    data = xml.splitlines()

    line = random.randint(0, len(data)-1)
    data[line] = '\t' + data[line]
    xml_str = lst_to_str(data)
    return xml_str

# Format string fuzzer checks FS vulnerability
# Replaces any links in tag <a href="???"> with "%s%s%s"
def format_string(xml: str):
    if ('href=\"' not in xml):
        return xml

    lines = xml.splitlines()
    i = 0
    for line in lines:
        if ("href=" in line):
            start, end, j = 0, 0, 0
            for char in line:
                if (char == '\"' and start == 0):
                    start = j + 1
                elif (char == '\"' and start):
                    end = j
                j += 1
            lines [i] = line[:start]  + '%s%s%s' + line[end:]
        i += 1

    xml_str = lst_to_str(lines)
    return xml_str

def insert_img(xml:str):
    tag = '<img src="https://misc0110.net/cysec_memes/ropchain.jpg" width="40" height="40">\n'
    pos = 1
    for char in xml:
        if char == '\n':
            return xml[:pos] + tag + xml[pos:]
        pos += 1
    return xml


def fuzz_xml(xml: str, q: Queue):
    xml_mutators = [
        rearrange_tags,
        add_root,
        remove_key_symbols,
        capitalise_random,
        add_symbols,
        modify_nesting,
        format_string,
        insert_img,
    ]

    
    for r in range(1, len(xml_mutators) + 1):  
        for mutator_combination in itertools.combinations(xml_mutators, r):  
            for mutator in mutator_combination:
                fuzzed_output = mutator(xml) 
                #print(fuzzed_output)
                #log.info("Currently mutatating using: {}".format(mutator))
            q.put(fuzzed_output)
    log.info('all combinations done in XML???')

def lst_to_str(lst):
    xml = ""
    for row in lst:
        xml += row + '\n'
    return xml
            

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
    with open('../assignment/xml_test.txt', 'r') as f:
        content = f.read() # pass input on as the file and convert it to content
        #root = et.fromstring(content)
    fuzzed_input = insert_img(content)

    q.put(fuzzed_input)
    run_binary("../assignment/xml3", q)
