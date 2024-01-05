#include <iostream>

struct testcase {
    long long a, b;

    void write(std::ostream& os) const {
        os << a << ' ' << b << '\n';
    }
};