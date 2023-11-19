 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>

 void parse_csv(char *input) {
    char *token = strtok(input, ",");

    while (token) {
        printf("%s\n", token);
        token = strtok(NULL, ",");
    }

 }

 int main() {
    char buffer[20];

    fgets(buffer, sizeof(buffer), stdin);

    parse_csv(buffer);

    return 0;
 }