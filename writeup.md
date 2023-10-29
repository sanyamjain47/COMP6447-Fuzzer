6447-FUZZER
========================
## Usage

```
python3 main.py <binary> <template>
```
------------------------

## Description

In our fuzzer, we take the binary that needs to be fuzzed and the template input that can be run against the binary.
It tries to detect the input either as CSV or JSON (Midpoint submission only requires these things).
The fuzzer then calls the appropriate method that runs the fuzzing ideas on the input. We have a base fuzzer that is generic to both csv and json. The other fuzzer is specific to JSON or CSV depending on the type. 

## Base/Generic

These are some generic fuzzing methods that are applied on every type. 

`bit_flip`: Randomly flips one to seven bits of a single character in the input string.
`delete_random_byte`: Removes a random substring from the input string.
`insert_random_byte`: Inserts a random string at a random position in the input string.
`append_random_num_bytes`: Appends a random number (1 to 50) of the same random ASCII character to the end of the input string .
`append_random_num_str`: Appends a randomly selected substring from the input string `s` to its end, repeated a random number (1 to 10) of times.

## CSV

The CSV fuzzer methods take in all the possible mutators for the csv and runs all the combination of it on the given input.
The mutators - 

- `inconsistent_data_types`: Alters a random cell in the CSV data to append 'abc', thereby creating inconsistent data types.
- `negative_numbers`: Converts a random numeric value in the CSV data to its negative form.
- `foreign_characters`: Inserts a random foreign character into a random cell in the CSV data.
- `extra_commas`: Appends three extra commas to a random cell in the CSV data.
- `nested_quotes`: Encloses a random cell's value in the CSV data within double quotes.
- `add_many_rows`: Duplicates a random row in the CSV data between 100 to 200 times and appends them to the existing data.

Then our main function - `generate_csv_fuzzed_output` creates all combinations of the given mutator functions and creates new input for the binary. These all inputs are fed to a queue to which our harness is listening to and running the binary against this.

## JSON

The structure of JSON fuzzer is similar to our CSV fuzzer. The current mutators in the JSON fuzzer are - 

- `strat1`: Appends an "A" to a random string value within the input dictionary.
- `strat2`: Wraps the entire dictionary in a nested dictionary up to a depth of 50.
- `strat3`: Replaces a random string value in the dictionary with a string consisting of 10,000 "A" characters.
- `strat4`: Replaces a random integer value in the dictionary with a randomly chosen extreme numerical value.
- `strat5`: Adds 1,000 key-value pairs to the dictionary, each key is a string like "key0", "key1", etc., and each value is a string like "value0", "value1", etc.
- `strat7`: Sets a random key's value in the dictionary to `None`.
- `strat9`: Replaces a random key's value in the dictionary with a null-like value based on its original type (empty string, 0, empty list, empty dictionary, etc.).

## Harness

Our `harness.py` file has a function called `run_binary_and_check_segfault` which is kept alive for `150 seconds`. It keeps on listening on the queue that is being populated by our both the fuzzers - base fuzzer and type specific. If the process exits with a segmentation fault (exit code -11), it triggers the `generate_report` function and terminates the program.
`generate_report`: This function writes a report to a file named 'bad.txt'. The report contains the input data that caused the segmentation fault and the associated error code.

## Next Objectives
- Add proper harnessing. 
The current harnessing is very slow and only looks for segfaults. The current harnessing is very slow as we are running subprocess for every input. 
- The current fuzzers only work a generated set of inputs. It needs to be able to further fuzz on fuzzed input to check for new things.
- Our main Fuzzer idea and structure is really good. We can easily extend it to support multiple types. If we can make our harnessing more powerful, we can gather much more stats and have a more complete fuzzer.