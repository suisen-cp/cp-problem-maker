#include <cassert>
#include <iostream>

int main() {
    long long x, y;
    std::cin >> x >> y;
    assert(x <= 1000000000);
    std::cout << x + y << std::endl;
}