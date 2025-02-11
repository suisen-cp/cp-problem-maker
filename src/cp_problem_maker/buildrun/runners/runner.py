import os
import resource
import subprocess
import sys
import time
from io import BytesIO, TextIOWrapper
from pathlib import Path
from threading import Thread
from typing import IO, Any, TextIO, TypedDict

import psutil
from pydantic import BaseModel, ConfigDict, Field

from cp_problem_maker.logging.setup import get_logger

logger = get_logger(__name__)

FileDescriptor = int
File = TextIO | BytesIO | TextIOWrapper | FileDescriptor


class RunnerParams(BaseModel):
    stdin: File = Field(
        default_factory=sys.stdin.fileno, description="Input stream for the command"
    )
    stdout: File = Field(
        default_factory=sys.stdout.fileno, description="Output stream for the command"
    )
    stderr: File = Field(
        default_factory=sys.stderr.fileno, description="Error stream for the command"
    )
    timeout: float | None = Field(
        None, description="Timeout for the command in seconds"
    )
    memory_limit: int | None = Field(
        None, description="Memory limit for the command in MiB"
    )
    check_returncode: bool = Field(
        ...,
        description="Check the returncode of the command. If True, an exception is raised if the exit code is non-zero",  # noqa: E501
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class RunResult(BaseModel):
    stdout: str
    stderr: str
    returncode: int
    elapsed_time: float
    """Elapsed time in seconds"""
    used_memory_mb: float
    """Memory usage in MiB"""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


def _limit_memory(max_memory_mb: int | None) -> None:
    """Limit the memory usage of the process

    Args:
        max_memory_mb (int | None): Maximum memory usage in MiB
    """
    if max_memory_mb is None:
        return
    if max_memory_mb <= 0:
        raise ValueError("Memory limit must be positive")
    try:
        max_memory_bytes = max_memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
    except OSError as e:
        raise RuntimeError(f"Failed to set memory limit: {e}") from e
    except AttributeError as e:
        raise NotImplementedError(
            "Memory limit setting is not supported on this platform"
        ) from e


class _MemoryUsageDict(TypedDict):
    rss: float


def monitor_memory(
    process: "subprocess.Popen[Any]", memory_usage_dict: _MemoryUsageDict
) -> None:
    """Monitor the memory usage of a process."""
    try:
        ps_process = psutil.Process(process.pid)
        max_memory_usage = 0
        while process.poll() is None:
            memory_info = ps_process.memory_info()
            max_memory_usage = max(max_memory_usage, memory_info.rss)
            time.sleep(0.01)
        memory_usage_dict["rss"] = max_memory_usage
    except psutil.NoSuchProcess:
        pass


def _dest(f: File) -> IO[Any]:
    if isinstance(f, FileDescriptor):
        fd: FileDescriptor = f
        if fd < 0:
            if fd == subprocess.STDOUT:
                return sys.stdout
            elif fd == subprocess.DEVNULL:
                return Path(os.devnull).open(mode="w")
            else:
                raise ValueError(f"Invalid file descriptor: {fd}")
        if fd == sys.stdout.fileno():
            return sys.stdout
        if fd == sys.stderr.fileno():
            return sys.stderr
        raise ValueError(f"Invalid file descriptor: {fd}")
    return f


def run(cmd: list[str], *, runner_params: RunnerParams) -> RunResult:
    """Run the command

    Args:
        cmd (list[str]): Command to run
        runner_params (RunnerParams): Parameter set for running the command
    Returns:
        str: Output of the command
    """
    logger.debug("Running command: %s", cmd)
    memory_usage_dict: _MemoryUsageDict = {"rss": 0}
    # Start the process
    with subprocess.Popen(
        cmd,
        stdin=runner_params.stdin,
        preexec_fn=lambda: _limit_memory(runner_params.memory_limit),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        memory_monitor = Thread(
            target=monitor_memory, args=(process, memory_usage_dict), daemon=True
        )
        memory_monitor.start()

        start_time = time.perf_counter_ns()
        try:
            stdout, stderr = process.communicate(timeout=runner_params.timeout)
        except subprocess.TimeoutExpired as e:
            process.kill()
            memory_monitor.join()
            assert runner_params.timeout is not None
            raise subprocess.TimeoutExpired(cmd, runner_params.timeout) from e
        except Exception as e:
            process.kill()
            memory_monitor.join()
            raise e
        end_time = time.perf_counter_ns()
        memory_monitor.join()

        run_result = RunResult(
            stdout=stdout,
            stderr=stderr,
            returncode=process.returncode,
            elapsed_time=(end_time - start_time) / 10**9,
            used_memory_mb=memory_usage_dict["rss"] / 1024 / 1024,
        )
    _dest(runner_params.stdout).write(run_result.stdout)
    _dest(runner_params.stderr).write(run_result.stderr)
    if runner_params.check_returncode and run_result.returncode:
        raise subprocess.CalledProcessError(
            returncode=run_result.returncode,
            cmd=cmd,
            output=run_result.stdout,
            stderr=run_result.stderr,
        )
    return run_result


class InteractiveJudgeParams(BaseModel):
    stderr: File = Field(
        default_factory=sys.stderr.fileno, description="Error stream for the command"
    )
    timeout: float | None = Field(
        None, description="Timeout for the command in seconds"
    )
    memory_limit: int | None = Field(
        None, description="Memory limit for the command in MiB"
    )

    judge_stderr: File = Field(
        default_factory=sys.stderr.fileno, description="Error stream for the command"
    )
    judge_timeout: float = Field(
        1.0,
        description="Timeout for the judge in seconds after the solver finishes running",  # noqa: E501
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )


class JudgeTimeoutExpired(subprocess.TimeoutExpired):
    pass


class SolverTimeoutExpired(subprocess.TimeoutExpired):
    pass


def run_interactive_judge(
    judge_cmd: list[str], solver_cmd: list[str], *, params: InteractiveJudgeParams
) -> RunResult:
    """Run the interactive judge

    Args:
        judge_cmd (list[str]): Command to run the judge
        solver_cmd (list[str]): Command to run the solver
        params (InteractiveJudgeParams): Parameter set for running the interactive judge
    Returns:
        RunResult:
            Result of the interactive judge.
            - `returncode` is the return code of the **judge**.
            - `elapsed_time` is the time taken by the **solver**.
            - `used_memory_mb` is the memory usage of the **solver**.
            - `stdout` and `stderr` are empty strings.
    Raises:
        subprocess.TimeoutExpired:
            If the solver or judge times out.
            - If the solver times out, the error message is `SOLVER_TLE_MESSAGE`.
            - If the judge times out, the error message is `JUDGE_TLE_MESSAGE`.
        subprocess.CalledProcessError:
            If the solver returns a non-zero exit
    """
    logger.debug("Running the interactive judge: %s", judge_cmd)
    logger.debug("Running the interactive solver: %s", solver_cmd)
    memory_usage_dict: _MemoryUsageDict = {"rss": 0}
    with subprocess.Popen(
        judge_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=_dest(params.judge_stderr),
        text=True,
    ) as p_judge:
        with subprocess.Popen(
            solver_cmd,
            stdin=p_judge.stdout,
            stdout=p_judge.stdin,
            stderr=_dest(params.stderr),
            text=True,
            preexec_fn=lambda: _limit_memory(params.memory_limit),
        ) as p_solver:
            memory_monitor = Thread(
                target=monitor_memory, args=(p_solver, memory_usage_dict), daemon=True
            )
            memory_monitor.start()

            start_time = time.perf_counter_ns()
            try:
                returncode_solver = p_solver.wait(timeout=params.timeout)
            except subprocess.TimeoutExpired as e:
                p_solver.kill()
                p_judge.kill()
                memory_monitor.join()
                assert params.timeout is not None
                raise SolverTimeoutExpired(solver_cmd, params.timeout) from e

            end_time = time.perf_counter_ns()
            memory_monitor.join()

            assert p_judge.stdin is not None
            p_judge.stdin.close()

            if returncode_solver:
                p_judge.kill()
                raise subprocess.CalledProcessError(
                    returncode=returncode_solver, cmd=solver_cmd
                )

            try:
                returncode_judge = p_judge.wait(timeout=params.judge_timeout)
            except subprocess.TimeoutExpired as e:
                p_judge.kill()
                raise JudgeTimeoutExpired(judge_cmd, params.judge_timeout) from e

            run_result = RunResult(
                stdout="",
                stderr="",
                returncode=returncode_judge,
                elapsed_time=(end_time - start_time) / 10**9,
                used_memory_mb=memory_usage_dict["rss"] / 1024 / 1024,
            )
    return run_result
