#include <stdio.h>
#include <roaring/roaring.h>

int main(void) {
    roaring_bitmap_t *bm = roaring_bitmap_create();
    roaring_bitmap_free(bm);
    return 0;
}
