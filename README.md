# cp-problem-maker

Tools for creating competitive programming problems.

**Interactive problems have not been supported yet.**

## Usage

```
usage: cp-problem-maker [-h] {check,config,gen-cases,gen-params,init,test} ...

Tools for creating competitive programming problems

positional arguments:
  {check,config,gen-cases,gen-params,init,test}
    check               Check the solutions
    config              Change the settings
    gen-cases           Generate test cases
    gen-params          Generate problem parameters
    init                Initialize a new project
    test                Test the problems; generating testcases and checking all the solutions

options:
  -h, --help            show this help message and exit
```

### `init`

```
usage: cp-problem-maker init [-h] [-p PATH] [--search-root]

Initialize a new project

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
  --search-root         Search for the root of the project
```

### `gen-params`

```
usage: cp-problem-maker gen-params [-h] [-p PATH]

Generate problem parameters

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
```

### `gen-cases`

```
usage: cp-problem-maker gen-cases [-h] [-p PATH] [--error-on-unused] [--no-update-params] [--no-check] [-i] [-s SOLVER]

Generate test cases

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
  --error-on-unused     Error on unused generators
  --no-update-params    Do not update the parameters
  --no-check            Do not check the answers
  -i, --interactive     Generate test cases for the interactive problem
  -s SOLVER, --solver SOLVER
                        Path to the answer generator.
```

### `check`

```
usage: cp-problem-maker check [-h] [--all] [-p PATH] [--no-stderr] [--interactive] [targets ...]

Check the solutions

positional arguments:
  targets               Targets to check

options:
  -h, --help            show this help message and exit
  --all                 Check all the solutions
  -p PATH, --path PATH  Path to the project
  --no-stderr           Suppress stderr of the solver and the checker
  --interactive, -i     Use interactive judge
```

### `test`

```
usage: cp-problem-maker test [-h] [-p PATH] [--no-stderr] [-i] [-s SOLVER]

Test the problems; generating testcases and checking all the solutions

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
  --no-stderr           Suppress stderr of the solver and the checker
  -i, --interactive     Use interactive judge
  -s SOLVER, --solver SOLVER
                        Path to the answer generator.
```

### `config`

```
usage: cp-problem-maker config [-h] [--space-separated] {global,local} key [value] [--values ...]

Change the settings

positional arguments:
  {global,local}     Scope of the option. Use 'global' for global settings, 'local' for local settings
  key                The key of the option. Use dot notation like 'language.cpp.flags'. Use '.' to display the entire configuration.
  value              The value of the option. If omitted, the current value will be retrieved.

options:
  -h, --help         show this help message and exit
  --space-separated  Get the value as a space-separated list (for list-type values).
  --values ...       Specify multiple values as a space-separated list for list-type options.
```
