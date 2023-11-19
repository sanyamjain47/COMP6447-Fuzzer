 #include <stdio.h>
 #include <stdlib.h>

 void parse_xml(char *input) {
    char buff[256];

    sscanf(input, "<data>%255[^<]", buff);
    printf("%s", buff);
 }

 int main() {
    char buffer[512];

    fgets(buffer, sizeof(buffer), stdin);

    parse_xml(buffer);
    
    return 0;
 }