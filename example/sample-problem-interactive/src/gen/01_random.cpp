#include <iostream>
#include <random>

#include "../params.h"

int main(int, char* argv[]) {
    // argv[1]: ID (Starts from 0 for each test case group)
    // argv[2]: Random seed (Generated from the test case group's name and the case's ID)
    int seed = ::atoi(argv[2]);
    std::mt19937 gen(seed);
    int w = N_MAX + 1 - N_MIN;
    int n = gen() % w + N_MIN;
    std::cout << n << '\n';
}
