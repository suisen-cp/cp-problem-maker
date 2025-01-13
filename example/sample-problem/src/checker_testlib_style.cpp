#include <cassert>
#include <fstream>
#include <iostream>

int main(int argc, char* argv[]) {
    assert(argc == 4);
    std::ifstream input(argv[1]);
    std::ifstream output(argv[2]);
    std::ifstream answer(argv[3]);

    // You can read the input, output (= contestant's output) and answer (= judge's output) files
    int x, y;
    input >> x >> y;
    int contestant_output;
    output >> contestant_output;
    int judge_output;
    answer >> judge_output;

    if (contestant_output == judge_output) {
        std::cerr << "AC" << std::endl;
        return 0;
    } else {
        std::cerr << "WA: expected = " << judge_output << ", actual = " << contestant_output << std::endl;
        return 1;
    }
}
