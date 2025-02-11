#include <testlib.h>
#include "params.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    inf.readInt(N_MIN, N_MAX);
    inf.readChar('\n');
    inf.readEof();

    return 0;
}
