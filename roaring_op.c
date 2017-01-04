#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <roaring/roaring.h>

static const int seed = 27;

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

unsigned long check_int(int *error, char *string, char *var_name) {
    unsigned long var = strtoul(string, NULL, 10);
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

roaring_bitmap_t *init_bitmap(unsigned long size, unsigned long universe, int copy_on_write, int run_containers) {
    roaring_bitmap_t *bm;

    if(size*2 < universe) { // we create an empty bitmap and then add values
        bm = roaring_bitmap_create();
        uint64_t cardinality = 0;
        while(cardinality < size) {
            for(int i = cardinality ; i < size ; i++) {
                uint32_t value = rand()%universe;
                roaring_bitmap_add(bm, value);
            }
            cardinality = roaring_bitmap_get_cardinality(bm);
        }
    }
    else { // we create a full bitmap and then remove values
        bm = roaring_bitmap_from_range(0, universe, 1);
        uint64_t cardinality = universe;
        while(cardinality > size) {
            for(int i = size ; i < cardinality ; i++) {
                uint32_t value = rand()%universe;
                roaring_bitmap_remove(bm, value);
            }
            cardinality = roaring_bitmap_get_cardinality(bm);
        }
    }
    assert(roaring_bitmap_get_cardinality(bm) == size);
    bm->copy_on_write = copy_on_write;
    if(run_containers) {
        roaring_bitmap_run_optimize(bm);
    }
    return bm;
}

double timeval_to_second(struct timeval time) {
    return (double)(time.tv_sec) + (double)(time.tv_usec)*1e-6;
}

double time_for_op(roaring_bitmap_t *bm1, roaring_bitmap_t *bm2) {
    struct timeval before = {};
    struct timeval after = {};

    gettimeofday(&before, NULL);
    roaring_bitmap_t *result = roaring_bitmap_or(bm1, bm2);
    gettimeofday(&after, NULL);

    roaring_bitmap_free(result);

    return timeval_to_second(after)-timeval_to_second(before);
}

int main(int argc, char *argv[]) {
    srand(seed);

    unsigned long size1, universe1, size2, universe2;
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

    roaring_bitmap_t *bm1 = init_bitmap(size1, universe1, copy_on_write, run_containers);
    roaring_bitmap_t *bm2 = init_bitmap(size2, universe2, copy_on_write, run_containers);

/*
    roaring_bitmap_printf(bm1);printf("\n");
    roaring_bitmap_printf(bm2);printf("\n");
*/

    double time = time_for_op(bm1, bm2);
    printf("%.8lf\n", time);

    roaring_bitmap_free(bm1);
    roaring_bitmap_free(bm2);

    return 0;
}
