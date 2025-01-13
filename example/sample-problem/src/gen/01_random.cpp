#include <iostream>
#include <random>

int main(int, char* argv[]) {
    // argv[1]: ID (Starts from 0 for each test case group)
    // argv[2]: Random seed (Generated from the test case group's name and the case's ID)
    int seed = ::atoi(argv[2]);
    std::mt19937 gen(seed);
    int x = gen() % 100;
    int y = gen() % 100;
    std::cout << x << ' ' << y << '\n';
}
