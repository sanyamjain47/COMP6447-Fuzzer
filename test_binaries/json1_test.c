 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <json-c/json.h>

void parse_json(char *input) {

    struct json_object *parsed_json = json_tokener_parse(input);

    char buffer[20];

    const char *json_string = json_object_get_string(parsed_json);

    if (!json_string) {
        printf("Invalid input.\n");
        exit(1);
    }

    size_t buffer_size = strlen(json_string);


    strncpy(buffer, json_string, buffer_size);

    json_object_put(parsed_json);
}


 int main() {
    // Set an arbitrary size for the input buffer
    #define MAX_INPUT_SIZE 1024
    char input[MAX_INPUT_SIZE];

    // if (argc != 2) {
    //     printf("Usage: %s <json_input>\n", argv[0]);
    //     return 1;
    // }

    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Error reading input.\n");
        return 1;
    }

    parse_json(input);

    return 0;
 }