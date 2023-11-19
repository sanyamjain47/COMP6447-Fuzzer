import itertools
from queue import Queue
import random
import subprocess
import sys
import xml.etree.ElementTree as et
from pwn import *
from harness import run_binary_string
from queue import Queue
from threading import Thread

# Global flag to indicate whether to terminate threads
terminate_threads_flag = False

# thread-safe int
function_count_lock = threading.Lock()
first_count = -1
base_input = None

##########################
## XML SPECIFIC METHODS ##
#########################
def lst_to_str(lst):
    xml = ""
    for row in lst:
        xml += row + '\n'
    return xml

def duplicate_tags(xml: str):
    data = xml.splitlines()
    # Find lines that contain XML tags
    tag_lines = [index for index, line in enumerate(data) if re.search(r'<[^>]+>', line)]

    # Proceed only if there are tag lines
    if tag_lines:
        index = random.choice(tag_lines)
        tag = data[index]
        # Inserting the duplicate tag right after the original
        data.insert(index + 1, tag)

    return '\n'.join(data)

def remove_random_tags(xml: str):
    data = xml.splitlines()
    # Regular expression to identify lines with tags
    tag_pattern = re.compile(r'<[^>]+>')

    # Find lines that contain tags
    tag_lines = [index for index, line in enumerate(data) if tag_pattern.search(line)]

    # Proceed only if there are tag lines
    if tag_lines:
        # Randomly select a tag line to remove
        index_to_remove = random.choice(tag_lines)
        del data[index_to_remove]

    return '\n'.join(data)

def random_attribute_injection(xml: str):
    data = xml.splitlines()
    # Regular expression to identify valid tags for attribute injection
    tag_pattern = re.compile(r'<[^!?][^>]*[^/]')

    # Find lines that contain valid tags
    valid_tag_lines = [index for index, line in enumerate(data) if tag_pattern.search(line)]

    # Inject attribute into randomly selected valid tags
    for index in valid_tag_lines:
        line = data[index]
        new_attr = f' randomAttr{random.randint(0, 100)}="value"'
        # Find the position to insert the new attribute
        insert_pos = line.rfind('>')
        data[index] = line[:insert_pos] + new_attr + line[insert_pos:]

    return '\n'.join(data)


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
    # Regular expression to identify lines with tags
    tag_pattern = re.compile(r'<[^>]+>')

    # Find lines that contain tags
    tag_lines = [index for index, line in enumerate(data) if tag_pattern.search(line)]

    # Proceed only if there are at least two tag lines
    if len(tag_lines) > 1:
        # Randomly select two different tag lines to swap
        index1, index2 = random.sample(tag_lines, 2)

        # Swapping tag1 and tag2 positions
        data[index1], data[index2] = data[index2], data[index1]

    return '\n'.join(data)

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

def insert_nested_tags(xml: str):
    nesting = '<new-tag class="nesting"></new-tag><div class="classy" id="1"><a class="classy" href="http://comp6447.lol">this link looks sus</a><link class="classy" href="http://comp6447.lol" /><span class="classy">text</span><link class="classy" href="http://comp6447.lol" /></div><div class="classy" data="when" name="adam" /><div class="classy"><a class="classy" href="http://comp6447.lol">this link looks sus</a><span class="classy">text</span><new-tag class="nesting"></new-tag><new-tag class="nesting"></new-tag></div><span class="classy" id="666">software engineers are questy</span><new-tag class="nesting"></new-tag><span class="classy" id="666"></span><new-tag class="nesting"></new-tag><span class="classy" id="666">software engineers are questy</span><fam class="classy" id="fam">nah</fam><div class="classy" id="90"><a class="classy" href="http://comp6447.lol">This link looks sus</a><link class="classy" href="http://comp6447.lol" /><span class="classy">text</span></div><new-tag class="nesting"></new-tag><fam class="classy" id="fam">cringe</fam><span class="classy" id="666">software engineers are questy</span><fam class="classy" id="fam">cringe</fam><new-tag class="nesting"></new-tag><new-tag class="nesting"></new-tag><div class="classy" id="90"><a class="classy" href="http://comp6447.lol">this link looks sus</a><link class="classy" href="http://comp6447.lol" /><span class="classy">text</span></div><new-tag class="nesting"></new-tag><new-tag class="nesting"></new-tag><link class="classy" href="http://comp6447.lol" /><new-tag class="nesting"></new-tag>'
    data = xml.splitlines()

    line1 = random.randint(1, len(data)-2)
    line2 = random.randint(1, len(data)-2)
    data[line1] = data[line1] + '\n\t' + nesting
    data[line2] = data[line2] + '\n\t' + nesting
    #print(lst_to_str(data))
    return lst_to_str(data)

def generate_xml_fuzzed_output(xml, fuzzed_queue, binary_path, output_queue):
    xml_mutators = [
        rearrange_tags,
        add_root,
        remove_key_symbols,
        capitalise_random,
        add_symbols,
        modify_nesting,
        format_string,
        duplicate_tags,
        remove_random_tags,
        random_attribute_injection,
        change_tag_names,
        break_tag_structure,
        insert_nested_tags
    ]

    all_possible_mutations = Queue()
    list_all_possible_mutations = []
    for count in range(10):  # Adjust this count as needed
        for r in range(1, len(xml_mutators) + 1):
            for mutator_combination in itertools.combinations(xml_mutators, r):
                all_possible_mutations.put(mutator_combination)
                list_all_possible_mutations.append(mutator_combination)

    # Start generator threads
    generator_threads = multi_threaded_generator_xml(all_possible_mutations, xml, fuzzed_queue, num_threads=20)

    # Start harness threads
    harness_threads = multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=20)


    loop_back_threads = multi_threaded_loop_back_generator(fuzzed_queue,output_queue, list_all_possible_mutations, num_threads=10)
    
    for thread in generator_threads + harness_threads + loop_back_threads:
        thread.join()

def multi_threaded_generator_xml(mutator_queue, input, fuzzed_queue, num_threads=5):
    threads = []

    def thread_target():
        count = 0
        start_time = time.time()
        time_limit = 160  # 150 seconds
        while True:
            new_time = time.time()
            if new_time - start_time > time_limit:
                return
            if not mutator_queue.empty():
                mutator_combination = mutator_queue.get()
                fuzzed_output = input
                for mutator in mutator_combination:
                    fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
                fuzzed_queue.put({"input": fuzzed_output, "mutator": mutator_combination})
            else:
                return

    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    
    return threads


def multi_threaded_harness(binary_path, fuzzed_queue, output_queue, num_threads=5):
    threads = []

    def thread_target():
        run_binary_string(binary_path, fuzzed_queue, output_queue)
        return

    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    return threads

def loop_back_generator(input_queue,output_queue, all_mutations):
    global first_count
    global base_input
    start_time = time.time()
    time_limit = 160  # 150 seconds

    while True:
        
        new_time = time.time()
        if new_time - start_time > time_limit:
            return
        if output_queue.empty():
            time.sleep(5)
        with function_count_lock:
            fuzzed_output = output_queue.get()['input']
            function_count = output_queue.get()['count']

            if first_count == -1:
                first_count = function_count
                base_input = fuzzed_output


        # Take all values from the output queue
        values_to_process = list(output_queue.get()['input'])
        values_to_process.append(fuzzed_output)
        # Mutate each value with the chosen mutator combination
        mutated_values = []
        for value_info in values_to_process:
            mutated_value = random.choice([value_info,base_input])
            mutator_combination = random.choice(all_mutations)

            for mutator in mutator_combination:
                try:
                    mutated_value = mutator(mutated_value)
                except:
                    continue
            mutated_values.append({"input": mutated_value, "mutator": mutator_combination})

        # Put the mutated values back into the queue
        for mutated_value_info in mutated_values:
            input_queue.put(mutated_value_info)

def multi_threaded_loop_back_generator(input_queue,output_queue, all_mutations, num_threads=5):
    threads = []

    def thread_target():
        loop_back_generator(input_queue,output_queue, all_mutations)
    for _ in range(num_threads):
        thread = threading.Thread(target=thread_target)
        threads.append(thread)
        thread.start()

    return threads
