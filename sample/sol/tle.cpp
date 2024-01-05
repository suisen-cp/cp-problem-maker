#include <iostream>
#include <cassert>

#pragma GCC optimize("O0")

long long add(long long x, long long y) {
    if (x == 0) return y;
    return add(x - 1, y + 1);
}

int main() {
    long long x, y;
    std::cin >> x >> y;
    std::cout << add(x, y) << std::endl;
}