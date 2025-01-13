#include <iostream>
#include <unistd.h>

int main() {
    int x, y;
    std::cin >> x >> y;
    std::cout << x - y << '\n';
    ::sleep(3);
}
