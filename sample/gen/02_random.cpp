#include <cassert>
#include <iostream>
#include <random>

#include "../include/params.hpp"
#include "../include/testcase.hpp"

int main(int, char* argv[]) {
    uint32_t seed = std::atoi(argv[2]);
    std::mt19937 rng{seed};
    std::uniform_int_distribution<long long> dist(0, N_MAX);
    long long a = dist(rng);
    long long b = dist(rng);
    testcase{ a, b }.write(std::cout);
}