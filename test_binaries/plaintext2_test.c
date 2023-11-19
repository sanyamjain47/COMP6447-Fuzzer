#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int main() {
    char buffer[20];
    gets(buffer);

    if (strlen(buffer) > sizeof(buffer)) {
        printf("Invalid input.\n");
        exit(1);
    }

    printf("%s", buffer);
    
    return 0;
}