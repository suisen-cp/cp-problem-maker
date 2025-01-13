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
    config              Change the global settings
    gen-cases           Generate test cases
    gen-params          Generate problem parameters
    init                Initialize a new project
    test                Test the problems; generating testcases and checking all the
                        solutions

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
usage: cp-problem-maker gen-cases [-h] [-p PATH] [--error-on-unused]

Generate test cases

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
  --error-on-unused     Error on unused generators
```

### `check`

```
usage: cp-problem-maker check [-h] [--all] [-p PATH] [--no-stderr] [targets ...]

Check the solutions

positional arguments:
  targets               Targets to check

options:
  -h, --help            show this help message and exit
  --all                 Check all the solutions
  -p PATH, --path PATH  Path to the project
  --no-stderr           Suppress stderr of the solver and the checker
```

### `test`

```
usage: cp-problem-maker test [-h] [-p PATH] [--no-stderr]

Test the problems; generating testcases and checking all the solutions

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the project
  --no-stderr           Suppress stderr of the solver and the checker
```

### `config`

```
usage: cp-problem-maker config [-h] {global,local} key [value]

Change the settings

positional arguments:
  {global,local}  Scope of the option. 'global' for global settings, 'local' for
                  local settings
  key             Key of the option. Keys are specified like 'language.cpp.flags'. If
                  set to '.', show the whole config.
  value           Value of the option. If not given, get the value of the option

options:
  -h, --help      show this help message and exit
```
