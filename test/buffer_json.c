 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <json-c/json.h>

void parse_json(char *input) {
    struct json_object *parsed_json = json_tokener_parse(input);

    char buffer[10];
    strcpy(buffer, json_object_get_string(parsed_json));

    json_object_put(parsed_json);
}


 int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <json_input>\n", argv[0]);
        return 1;
    }

    char *input = argv[1];
    parse_json(input);

    return 0;
 }