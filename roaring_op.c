#include <stdio.h>
#include <stdlib.h>
#include <time.h>
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

void fill_bitmap(roaring_bitmap_t *bm, long size, long universe, int copy_on_write, int run_containers) {
    uint64_t cardinality = 0;

    while(cardinality < size) {
        for(int i = cardinality ; i < size ; i++) {
            uint32_t value = rand()%universe;
            roaring_bitmap_add(bm, value);
        }
        cardinality = roaring_bitmap_get_cardinality(bm);
    }

    bm->copy_on_write = copy_on_write;
    if(run_containers) {
        roaring_bitmap_run_optimize(bm);
    }
}

double time_for_op(roaring_bitmap_t *bm1, roaring_bitmap_t *bm2) {
    struct timespec stop, start;
    if(clock_gettime(CLOCK_REALTIME, &start) != 0) {
        perror("clock_gettime");
        exit(1);
    }
    roaring_bitmap_t *result = roaring_bitmap_or(bm1, bm2);
    if(clock_gettime(CLOCK_REALTIME, &stop) != 0) {
        perror("clock_gettime");
        exit(1);
    }

    double total_time = (double)(stop.tv_sec-start.tv_sec) + ((double)(stop.tv_nsec-start.tv_nsec))*1e-9;
    roaring_bitmap_free(result);
    return total_time;
}

int main(int argc, char *argv[]) {
    srand(time(NULL));

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
    roaring_bitmap_t *bm1 = roaring_bitmap_create();
    roaring_bitmap_t *bm2 = roaring_bitmap_create();

    fill_bitmap(bm1, size1, universe1, copy_on_write, run_containers);
    fill_bitmap(bm2, size2, universe2, copy_on_write, run_containers);

/*
    roaring_bitmap_printf_describe(bm1);printf("\n");
    roaring_bitmap_printf_describe(bm2);printf("\n");
*/

    double time = time_for_op(bm1, bm2);
    printf("%.8lf\n", time);

    roaring_bitmap_free(bm1);
    roaring_bitmap_free(bm2);

    return 0;
}
