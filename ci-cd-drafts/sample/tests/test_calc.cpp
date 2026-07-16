#include "calc.hpp"
#include <cstdio>

int main() {
    int failures = 0;

    if (calc::add(2, 3) != 5) {
        std::printf("FAIL: add(2,3) != 5\n");
        ++failures;
    }
    if (calc::multiply(4, 5) != 20) {
        std::printf("FAIL: multiply(4,5) != 20\n");
        ++failures;
    }

    if (failures == 0) {
        std::printf("all tests passed\n");
    }
    return failures == 0 ? 0 : 1;
}
