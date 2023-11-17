import itertools
from queue import Queue
import random
import subprocess
import sys
import xml.etree.ElementTree as et
from pwn import *
from harness import run_binary_and_check_segfault
from queue import Queue
from threading import Thread
##########################
## XML SPECIFIC METHODS ##
#########################

def duplicate_tags(xml: str):
    data = xml.splitlines()
    index = random.randrange(len(data))
    tag = data[index]
    # Inserting the duplicate tag right after the original
    data.insert(index + 1, tag)
    return lst_to_str(data)

def remove_random_tags(xml: str):
    data = xml.splitlines()
    if len(data) > 1:
        index = random.randrange(len(data))
        del data[index]
    return lst_to_str(data)

def random_attribute_injection(xml: str):
    data = xml.splitlines()
    for i, line in enumerate(data):
        start = line.find('<')
        end = line.find('>')
        # Check if it's a valid tag and not a closing tag
        if start != -1 and end != -1 and '/' not in line[start:end]:
            new_attr = f' randomAttr{random.randint(0, 100)}="value"'
            # Insert the new attribute just before the closing '>'
            data[i] = line[:end] + new_attr + line[end:]
    return lst_to_str(data)



def change_tag_names(xml: str):
    data = xml.splitlines()
    for i, line in enumerate(data):
        if '<' in line and '>' in line:
            start = line.find('<') + 1
            end = line.find('>')
            if start < end:
                new_tag = "randomTag" + str(random.randint(0, 100))
                data[i] = line[:start] + new_tag + line[end:]
    return lst_to_str(data)

def break_tag_structure(xml: str):
    data = xml.splitlines()
    if len(data) > 0:
        index = random.randrange(len(data))
        tag = data[index]
        if '<' in tag and '>' in tag:
            # Break the tag by removing its closing '>'
            data[index] = tag.replace('>', '', 1)
    return lst_to_str(data)

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
    new_root_tag = "newroot"
    return f"<{new_root_tag}>{xml}</{new_root_tag}>"


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

def generate_xml_fuzzed_output(xml, fuzzed_queue, binary_path):
    xml_mutators = [
        rearrange_tags,
        add_root,
        remove_key_symbols,
        capitalise_random,
        add_symbols,
        modify_nesting,
        format_string,
        insert_img,
        duplicate_tags,
        remove_random_tags,
        random_attribute_injection,
        change_tag_names,
        break_tag_structure
    ]

    all_possible_mutations = Queue()
    for count in range(10):  # Adjust this count as needed
        for r in range(1, len(xml_mutators) + 1):
            for mutator_combination in itertools.combinations(xml_mutators, r):
                all_possible_mutations.put(mutator_combination)

    # Start generator threads
    generator_threads = multi_threaded_generator_xml(all_possible_mutations, xml, fuzzed_queue, num_threads=10)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, num_threads=10)

    # Wait for all generator and harness threads to complete
    for thread in generator_threads + harness_threads:
        thread.join()

def multi_threaded_generator_xml(mutator_queue, input_xml, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        generator_xml(mutator_queue, input_xml, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads

def generator_xml(mutator_queue, input_xml, fuzzed_queue):
    while True:
        if not mutator_queue.empty():
            mutator_combination = mutator_queue.get()
            fuzzed_output = input_xml
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)
            fuzzed_queue.put({"input":fuzzed_output,"mutator":mutator_combination})
        else:
            return

def multi_threaded_harness(binary_path, fuzzed_queue, num_threads=5):
    threads = []
    def thread_target():
        run_binary_and_check_segfault(binary_path, fuzzed_queue)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()
    return threads

def lst_to_str(lst):
    xml = ""
    for row in lst:
        xml += row + '\n'
    return xml
            

if __name__ == "__main__":
    q = Queue()
    with open('../assignment/xml_test.txt', 'r') as f:
        content = f.read() # pass input on as the file and convert it to content
        #root = et.fromstring(content)
    fuzzed_input = insert_img(content)

    q.put(fuzzed_input)
    # run_binary("../assignment/xml3", q)
