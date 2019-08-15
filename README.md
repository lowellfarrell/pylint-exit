# pylint-exit-options


Utility to handle pylint exit codes on Linux in a scripting-friendly way.

Pylint uses bit-encoded exit codes to convey the results of the pylint review,
which means it will return with a non-zero return code even when the
pylint scoring was successful.

This can make it difficult to script the execution of pylint while at the same time
detecting genuine errors.

`pylint-exit-options` is a small command-line utility that can be used to re-process
the pylint return code and translate it into a scripting-friendly return code.

`pylint-exit-options` will decode the bit-encoded return code, identify whether there were
any fatal messages issued (which might constitute a failure in the execution of
pylint), or a usage error, and return a `0` or `1` return code that is more easily
used in shell scripts.

# Installation

You can manually install by downloading `pylint_exit_options.py`, and make it executable.

```bash
curl -o pylint-exit-options https://raw.githubusercontent.com/lowellfarrell/pylint-exit-options/master/pylint_exit_options.py && chmod +x pylint_exit_options.py
```

You should also consider creating a symbolic link so that the calls in the remainder of this
README work as described.  Update `<path-to>` with where you downloaded the script.

```bash
ln -s <path-to>/pylint_exit_options.py /usr/local/bin/pylint-exit-options
```

*Note: If you perform a `--user` install with `pip` then you will need to ensure `~/.local/bin` appears in your `PATH`
environment variable, otherwise the command line `pylint-exit-options` will not work.* 

# Usage
Add `|| pylint-exit-options $?` to the end of your existing Pylint command.  You can then
use the updated `$?` return code in your shell script.

```bash
pylint mymodule.py || pylint-exit-options $?
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi
```
# Options
--exit-report <F,E,W,R,C,U>
    You can choose which issue codes are part of the exit code with this option using a comma delimited 
string. Acceptable values are : F[Fatal], E[Error], W[Warning], R[Refactor], C[Convention], U[Usage]. 

usage: "-r=R" will report only Refactor type error codes, "-r=R,C" will report only Refactor and Convention 
type error codes. By default Fatal, Error, Warning and Usage type error codes are reported

# Example
In this example pylint detects convention issue(s), and exits with a return code of 16.  `pylint-exit-options` 
decodes this, displays the messages, and exits with a return code of 0.

```bash
> pylint pylint-exit-options.py || pylint-exit-options $?
pylint-exit-options.py:1:0: C0103: Module name "pylint-exit-options" doesn't conform to snake_case naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

The following types of issues were found:

  - convention message issued

Exiting gracefully...

> echo $?
0
```

In this example pylint detects convention issue(s), and exits with a return code of 16.  `pylint-exit-options` 
decodes this, displays the messages, and exits with a return code of 16.
```bash
> pylint pylint-exit-options.py || pylint-exit-options --exit-report=C $?
************* Module pylint-exit-options
pylint-exit-options.py:1:0: C0103: Module name "pylint-exit-options" doesn't conform to snake_case naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

The following types of issues were found:

  - convention message issued

The following types of issues are blocking:

  - convention message issued

Exiting due to issues...

> echo $?
16
```

# Default issue code convertions
Pylint can return combinations of the following codes.  `pylint-exit-options` will identify each
issued message, and return the bit wise sum of the issue codes as a final return code.

| Pylint code | Message | Final return code |
| ----------- | ------- | ----------------- |
| 1  | Fatal message issued | 1 |
| 2  | Error message issued | 2 |
| 4  | Warning message issued | 4 |
| 8  | Refactor message issued | 0 |
| 16 | Convention message issued | 0 |
| 32 | Usage error | 32 |

# Credit
Forked from: https://github.com/jongracecox/pylint-exit and https://github.com/theunkn0wn1/pylint-exit

