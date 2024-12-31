from pathlib import Path

from cp_problem_maker.buildrun.runners import runner
from tests.helpers.files import temp_files


def compile_cpp(cpp_file: Path, cpp_code: str) -> Path:
    cpp_file.write_text(cpp_code)
    exe_file = cpp_file.with_suffix("")
    with temp_files(3) as (stdin, stdout, stderr):
        runner.run(
            ["g++", "-std=c++17", "-o", f"{exe_file}", f"{cpp_file}"],
            runner_params=runner.RunnerParams(
                stdin=stdin, stdout=stdout, stderr=stderr, check_returncode=True
            ),
        )
    return exe_file
