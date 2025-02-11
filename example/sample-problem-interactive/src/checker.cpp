#include <testlib.h>

#include <iostream>

#include "params.h"

constexpr int B = 7;

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    const int X = inf.readInt();

    for (int num = 1;; ++num) {
        std::string t = ouf.readToken();
        ensure(t == "?" or t == "!");
        if (t == "?") {
            if (num > B) {
                std::cout << -1 << std::endl;
                quitf(_wa, "Too many questions");
            }
            int v = ouf.readInt(N_MIN, N_MAX);
            if (X < v) {
                std::cout << 1 << std::endl;
            } else {
                std::cout << 0 << std::endl;
            }
        } else {
            int v = ouf.readInt(N_MIN, N_MAX);
            if (X == v) {
                std::cout << 1 << std::endl;
                quitf(_ok, "Guessed the number in %d questions", num - 1);
            } else {
                std::cout << -1 << std::endl;
                quitf(_wa, "Guessed the wrong number");
            }
        }
    }
    quitf(_fail, "Unreachable");
}
