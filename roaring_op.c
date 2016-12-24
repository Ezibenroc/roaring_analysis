#include <stdio.h>
#include <stdlib.h>
#include <roaring/roaring.h>

void syntax(char *exec_name) {
    fprintf(stderr, "Syntax: %s <size1> <universe1> <size2> <universe2> <copy_on_write> <run_containers>\n", exec_name);
    fprintf(stderr, "\t<size1>          : integer, size of the first bitmap\n");
    fprintf(stderr, "\t<universe1>      : integer, universe size of the first bitmap\n");
    fprintf(stderr, "\t<size2>          : integer, size of the second bitmap\n");
    fprintf(stderr, "\t<universe2>      : integer, universe size of the second bitmap\n");
    fprintf(stderr, "\t<copy_on_write>  : {0, 1}, enable or not copy on write of the containers\n");
    fprintf(stderr, "\t<run_containers> : {0, 1}, enable or not the use of run containers\n");
    exit(1);
}

long check_int(int *error, char *string, char *var_name) {
    long var = atoi(string);
    if(var <= 0) {
        fprintf(stderr, "[ERROR] Expected a positive integer for %s, got %s\n", var_name, string);
        *error = 1;
    }
    return var;
}

int check_bool(int *error, char *string, char *var_name) {
    if((string[0] != '0' && string[0] != '1') || string[1] != '\0') {
        fprintf(stderr, "[ERROR] Expected a value in {0, 1} for %s, got %s\n", var_name, string);
        *error = 1;
    }
    return string[0] - '0';
}

int main(int argc, char *argv[]) {
    roaring_bitmap_t *bm = roaring_bitmap_create();
    roaring_bitmap_free(bm);

    long size1, universe1, size2, universe2;
    int copy_on_write, run_containers;
    int error = 0;

    if(argc != 7)
        syntax(argv[0]);

    size1          = check_int (&error, argv[1], "size1");
    universe1      = check_int (&error, argv[2], "universe1");
    size2          = check_int (&error, argv[3], "size2");
    universe2      = check_int (&error, argv[4], "universe2");
    copy_on_write  = check_bool(&error, argv[5], "copy_on_write");
    run_containers = check_bool(&error, argv[6], "run_containers");
    
    if(error)
        syntax(argv[0]);

/*
    printf("size1         : %ld\n", size1);
    printf("universe1     : %ld\n", universe1);
    printf("size2         : %ld\n", size2);
    printf("universe2     : %ld\n", universe2);
    printf("copy_on_write : %d\n", copy_on_write);
    printf("run_containers: %d\n", run_containers);
*/

    return 0;
}
