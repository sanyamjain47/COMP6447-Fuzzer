#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <elf.h>

void print_symbols(char *file_path) {
    FILE *file = fopen(file_path, "rb");

    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    Elf64_Ehdr elf_header;
    fread(&elf_header, sizeof(Elf64_Ehdr), 1, file);

    if (memcmp(elf_header.e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Not an ELF file\n");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Allocate memory for section headers
    Elf64_Shdr *section_headers = malloc(elf_header.e_shentsize * elf_header.e_shnum);
    if (section_headers == NULL) {
        perror("Error allocating memory");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read section headers
    fseek(file, elf_header.e_shoff, SEEK_SET);
    fread(section_headers, elf_header.e_shentsize, elf_header.e_shnum, file);

    printf("Symbols in %s:\n", file_path);

    for (int i = 0; i < elf_header.e_shnum; ++i) {
        if (section_headers[i].sh_type == SHT_SYMTAB || section_headers[i].sh_type == SHT_DYNSYM) {
            // Allocate memory for symbols
            Elf64_Sym *symbols = malloc(section_headers[i].sh_size);
            if (symbols == NULL) {
                perror("Error allocating memory");
                fclose(file);
                free(section_headers);
                exit(EXIT_FAILURE);
            }

            // Read symbols
            fseek(file, section_headers[i].sh_offset, SEEK_SET);
            fread(symbols, section_headers[i].sh_size, 1, file);

            int symbol_count = section_headers[i].sh_size / sizeof(Elf64_Sym);

            for (int j = 0; j < symbol_count; ++j) {
                // Check if the symbol name offset is within bounds
                if (symbols[j].st_name < section_headers[i].sh_size) {
                    printf("%lx %s\n", symbols[j].st_value, file_path + section_headers[i].sh_offset + symbols[j].st_name);
                }
            }

            free(symbols);
        }
    }

    free(section_headers);
    fclose(file);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <elf_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    char *file_path = argv[1];

    print_symbols(file_path);

    return 0;
}
