#include <cassert>
#include <fstream>
#include <iostream>

int main(int argc, char* argv[]) {
    assert(argc == 3);
    std::ifstream input(argv[1]);
    std::ifstream answer(argv[2]);

    // You can read the input and answer (= judge's output) files
    int x, y;
    input >> x >> y;
    int judge_output;
    answer >> judge_output;
    // In yukicoder style, the contestant's output is read from stdin
    int contestant_output;
    std::cin >> contestant_output;

    if (contestant_output == judge_output) {
        std::cerr << "AC" << std::endl;
        return 0;
    } else {
        std::cerr << "WA: expected = " << judge_output << ", actual = " << contestant_output << std::endl;
        return 1;
    }
}
