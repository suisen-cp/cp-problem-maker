#include "testlib.h"
#include "include/params.hpp"

int main() {
    registerValidation();

    inf.readLong(0, N_MAX, "A");
    inf.readSpace();
    inf.readLong(0, N_MAX, "B");
    inf.readChar('\n');
    inf.readEof();

    return 0;
}