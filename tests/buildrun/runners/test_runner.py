import subprocess
from pathlib import Path

import pytest

from cp_problem_maker.buildrun.runners import runner
from tests.helpers.compile import compile_cpp
from tests.helpers.files import temp_files


@pytest.mark.parametrize("n", [10**7, 2 * 10**7])
def test_run_memory_usage(cpp_file: Path, n: int) -> None:
    cpp_code = f"""
#include <chrono>
#include <cstdint>
#include <iostream>
#include <thread>
#include <random>
#include <vector>

int main() <%
    std::mt19937_64 rng;
    std::vector<int64_t> a({n});
    for (auto &e : a) e = rng();
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    int64_t X = 0;
    for (auto e : a) X ^= e;
    std::cout << X << std::endl;
%>
"""
    exe_file = compile_cpp(cpp_file, cpp_code)
    with temp_files(3) as (stdin, stdout, stderr):
        run_result = runner.run(
            [f"{exe_file}"],
            runner_params=runner.RunnerParams(
                stdin=stdin, stdout=stdout, stderr=stderr, check_returncode=True
            ),
        )
    expected_mb = n * 8 / 1024 / 1024
    assert abs(run_result.used_memory_mb - expected_mb) <= 5


def test_run_memory_exceeded(cpp_file: Path) -> None:
    cpp_code = """
#include <cstdint>
#include <vector>
int main() <% std::vector<int64_t> a(200000); %>
"""
    exe_file = compile_cpp(cpp_file, cpp_code)
    with temp_files(3) as (stdin, stdout, stderr):
        with pytest.raises(subprocess.CalledProcessError):
            runner.run(
                [f"{exe_file}"],
                runner_params=runner.RunnerParams(
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    check_returncode=True,
                    memory_limit=1,
                ),
            )


def test_run_timeout(cpp_file: Path) -> None:
    cpp_code = """
#include <chrono>
#include <thread>

int main() <%
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
%>
"""
    exe_file = compile_cpp(cpp_file, cpp_code)
    with pytest.raises(subprocess.TimeoutExpired):
        with temp_files(3) as (stdin, stdout, stderr):
            runner.run(
                [f"{exe_file}"],
                runner_params=runner.RunnerParams(
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=0.01,
                    check_returncode=False,
                ),
            )


@pytest.mark.parametrize("n, m", [(1, 2), (3, 4)])
def test_run_pipe(py_file: Path, n: int, m: int) -> None:
    py_code = """
import sys
n, m = map(int, input().split())
print(n + m, file=sys.stdout)
print(n * m, file=sys.stderr)
"""
    py_file.write_text(py_code)
    with temp_files(3) as (stdin, stdout, stderr):
        stdin.write(f"{n} {m}\n")
        stdin.seek(0)
        run_result = runner.run(
            ["python3", f"{py_file}"],
            runner_params=runner.RunnerParams(
                stdin=stdin, stdout=stdout, stderr=stderr, check_returncode=True
            ),
        )
    assert run_result.stdout.strip() == str(n + m)
    assert run_result.stderr.strip() == str(n * m)


def test_run_check_returncode_raise(py_file: Path) -> None:
    py_file.write_text("exit(1)")
    with temp_files(3) as (stdin, stdout, stderr):
        with pytest.raises(subprocess.CalledProcessError):
            runner.run(
                ["python3", f"{py_file}"],
                runner_params=runner.RunnerParams(
                    stdin=stdin, stdout=stdout, stderr=stderr, check_returncode=True
                ),
            )


def test_run_check_returncode_not_raise(py_file: Path) -> None:
    py_file.write_text("exit(1)")
    with temp_files(3) as (stdin, stdout, stderr):
        runner.run(
            ["python3", f"{py_file}"],
            runner_params=runner.RunnerParams(
                stdin=stdin, stdout=stdout, stderr=stderr, check_returncode=False
            ),
        )
