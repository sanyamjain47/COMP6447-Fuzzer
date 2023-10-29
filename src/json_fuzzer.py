import itertools
import json
from harness import run_binary_and_check_segfault


##########################
## JSON SPECIFIC METHODS ##
##########################

# ADD JSON FUZZ STRATS HERE

def generate_json_fuzzed_output(df, q):
    json_mutator = [
        
    ]
    df =  json.loads(df)

    for r in range(1, len(json_mutator) + 1):  # r ranges from 1 to the number of base mutators
        for mutator_combination in itertools.combinations(json_mutator, r):  # All combinations of size r
            fuzzed_output = df
            for mutator in mutator_combination:
                fuzzed_output = mutator(fuzzed_output)  # Apply each mutator in the combination to the string
            
            json_string = json.dumps(fuzzed_output)

            q.put(json_string)

    
