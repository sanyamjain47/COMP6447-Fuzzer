import threading
import queue
import time

# Parent class
class BaseFuzzer:
    def give_basic_fuzz(self, fuzzed_input):
        print("Giving basic fuzz")
        for i in range(5):
            fuzzed_input.put(f"Fuzz data {i}")

# Child class
class JSONFuzzer(BaseFuzzer, threading.Thread):
    def __init__(self, fuzzed_input, binary_output):
        threading.Thread.__init__(self)
        self.fuzzed_input = fuzzed_input
        self.binary_output = binary_output

    def run(self):
        print("JSONFuzzer thread started")
        
        # Call the parent class method
        self.give_basic_fuzz(self.fuzzed_input)
        
        while True:
            if not self.fuzzed_input.empty():
                item = self.fuzzed_input.get()
                print(f"JSONFuzzer: Popped {item} from fuzzed_input")
                
            print("JSONFuzzer: Pushing to binary_output")
            self.binary_output.put("Processed data")
            time.sleep(1)

# Master class to manage threads
class MasterFunction:
    def __init__(self, fuzzed_input, binary_output):
        self.fuzzed_input = fuzzed_input
        self.binary_output = binary_output

    def start_threads(self, thread_count=3):
        threads = []
        for i in range(thread_count):
            t = JSONFuzzer(self.fuzzed_input, self.binary_output)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

if __name__ == "__main__":
    fuzzed_input = queue.Queue()
    binary_output = queue.Queue()
    
    master_function = MasterFunction(fuzzed_input, binary_output)
    master_function.start_threads()
