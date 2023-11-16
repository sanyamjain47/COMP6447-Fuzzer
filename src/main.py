import sys
from pwn import *
import file_type
from main_fuzzer import start_csv,start_json, start_general, start_xml

if __name__ == "__main__":
    
    # print(sys.argv)
    if (len(sys.argv) != 3):
        print(f"Usage: python3 main,.py <Binary Path> <Template Path>")
        exit()

    bin_path = sys.argv[1]
    temp_path = sys.argv[2]
    if not file_type.check_file(bin_path,'x') or not file_type.check_file(temp_path,'r'):
        exit()
    
    payload = ""

    payload,type_file = file_type.read_and_determine_data(temp_path)
    print(payload, type_file)
    if type_file == 'CSV':
        log.info('Going into csv with {}, {}'.format(payload, bin_path) )
        start_csv(payload, bin_path)
    elif type_file == 'JSON':
        log.info('Going into json with {}, {}'.format(payload, bin_path) )
        start_json(payload, bin_path)
    elif type_file == 'XML':
        log.info('Going into xml with {}, {}'.format(payload, bin_path) )
        start_xml(payload, bin_path)
    else: 

        log.info('Going into generic with {}, {}'.format(payload, bin_path) )
        start_general(payload, bin_path)


