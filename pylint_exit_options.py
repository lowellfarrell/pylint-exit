#!/usr/local/bin/python3
"""
The goal of this script to add a level of customizability to exit handling for pylint
"""
from __future__ import print_function

import argparse
import sys

from bitarray import bitarray

# Package information
VERSION = __version__ = "0.1.1rc1"
__FATAL__ = 1
__ERROR__ = 2
__WARNING__ = 4
__REFACTOR__ = 8
__CONVENTION__ = 16
__USAGE__ = 32
__SUPPRESS__ = 0
__title__ = "pylint_exit_options"
__summary__ = "Exit code handler for pylint command line utility."
__uri__ = "https://github.com/lowellfarrell/pylint-exit-options"

EXIT_CODE_DEFAULTS = [
    (__FATAL__, 'fatal message issued', __FATAL__),
    (__ERROR__, 'error message issued', __ERROR__),
    (__WARNING__, 'warning message issued', __WARNING__),
    (__REFACTOR__, 'refactor message issued', __SUPPRESS__),
    (__CONVENTION__, 'convention message issued', __SUPPRESS__),
    (__USAGE__, 'usage error', __USAGE__)
]


def decode(value):
    """
    Decode the return code value into a bit array.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        list of raised exit codes.

    Example:
        >>> decode(1)
        [(1, 'fatal message issued', 1)]
        >>> decode(2)
        [(2, 'error message issued', 0)]
        >>> decode(3)
        [(1, 'fatal message issued', 1), (2, 'error message issued', 0)]
    """
    return [x[1] for x in zip(bitarray(bin(value)[2:])[::-1], EXIT_CODE_DEFAULTS) if x[0]]


def get_messages(value):
    """
    Return a list of raised messages for a given pylint return code.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        list of str: Raised messages.

    Example:
        >>> get_messages(1)
        ['fatal message issued']
        >>> get_messages(2)
        ['error message issued']
        >>> get_messages(3)
        ['fatal message issued', 'error message issued']
    """
    return [x[1] for x in decode(value)]


def get_exit_code(value):
    """
    Return the exist code that should be returned.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        int: Return code that should be returned when run as a command.

    Example:
        >>> get_exit_code(1)
        1
        >>> get_exit_code(2)
        2
        >>> get_exit_code(3)
        3
        >>> get_exit_code(12)
        4
    """
    exit_codes = [x[2] for x in decode(value)]
    if not exit_codes:
        return 0
    return sum(exit_codes)


def show_workings(value):
    """
    Display workings

    Args:
        value(int): Return code from pylint command line.

    Example:
        >>> show_workings(1)
        1 (1) = ['fatal message issued']
        >>> show_workings(12)
        12 (1100) = ['warning message issued', 'refactor message issued']
    """
    print("%s (%s) = %s" %
          (value, bin(value)[2:], [x[1][1] for x in zip(bitarray(bin(value)[2:])[::-1], EXIT_CODE_DEFAULTS) if x[0]]))


def handle_exit_code(value):
    """
    Exit code handler.

    Takes a pylint exist code as the input parameter, and
    displays all the relevant console messages.

    Args:
        value(int): Return code from pylint command line.

    Returns:
        int: Return code that should be returned when run as a command.

    Example:
        >>> handle_exit_code(1)
        The following messages were raised:
        <BLANKLINE>
          - fatal message issued
        <BLANKLINE>
        Fatal messages detected.  Failing...
        1
        >>> handle_exit_code(12)
        The following messages were raised:
        <BLANKLINE>
          - warning message issued
          - refactor message issued
        <BLANKLINE>
        No fatal messages detected.  Exiting gracefully...
        0
    """
    messages = get_messages(value)
    exit_code = get_exit_code(value)

    if messages:
        print('The following types of issues were found:')
        print('')

        for message in messages:
            print("  - %s" % message)

        print('')

    if exit_code:
        print('The following types of issues are blocker:')
        print('')

        exit_messages = get_messages(exit_code)
        for exit_message in exit_messages:
            print("  - %s" % exit_message)

        print('')
        print('Exiting with issues...')
    else:
        print('Exiting gracefully...')

    return exit_code


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument('pylint_exit_code', metavar='PYLINTRC', type=int,
                        help='pylint return code')
    suppress_exit_code_help = 'You can choose which issue codes are part of the exit code with this option.  ' \
                              'Acceptable values are : F[Fatal], E[Error], W[Warning], R[Refactor], C[Convention],' \
                              ' U[Usage]. Examples:   "-r=R" will report only Refactor type error codes, "-r=R,C" ' \
                              'will report only Refactor and Convention type error codes.  By default' \
                              ' Fatal, Error, Warning and Usage type error codes are reported'
    parser.add_argument('--exit-report', metavar='<F,E,W,R,C,U>', default='F,E,W,U', help=suppress_exit_code_help)

    return parser.parse_args()


def apply_enforcement_setting(key, value):
    """
    Apply an enforcement setting

    Args:
        key (int): specific message level to set
        value (int): new value for level

    """
    positions = {
        __FATAL__: 0,
        __ERROR__: 1,
        __WARNING__: 2,
        __REFACTOR__: 3,
        __CONVENTION__: 4,
        __USAGE__: 5
    }
    # fetch the position from the dict
    position = positions[key]

    # unpack the tuple so it can be modified
    encoded, description, enforce = EXIT_CODE_DEFAULTS[position]
    enforce = value  # set the element to True (error)

    # repack it back into a tuple to match existing data type
    EXIT_CODE_DEFAULTS[position] = encoded, description, enforce


def handle_cli_flags(namespace):
    """
    Applies the CLI flags

    Args:
        namespace (argparse.Namespace): namespace from CLI arguments

    """
    if namespace.exit_report:
        arg_value_list = namespace.exit_report.split(',')
        _set_report_arg_values(arg_value_list)


def _set_report_arg_values(arg_values: []):
    if 'F' in arg_values:
        apply_enforcement_setting(__FATAL__, __FATAL__)
    else:
        apply_enforcement_setting(__FATAL__, __SUPPRESS__)
    if 'E' in arg_values:
        apply_enforcement_setting(__ERROR__, __ERROR__)
    else:
        apply_enforcement_setting(__ERROR__, __SUPPRESS__)
    if 'W' in arg_values:
        apply_enforcement_setting(__WARNING__, __WARNING__)
    else:
        apply_enforcement_setting(__WARNING__, __SUPPRESS__)
    if 'R' in arg_values:
        apply_enforcement_setting(__REFACTOR__, __REFACTOR__)
    else:
        apply_enforcement_setting(__REFACTOR__, __SUPPRESS__)
    if 'C' in arg_values:
        apply_enforcement_setting(__CONVENTION__, __CONVENTION__)
    else:
        apply_enforcement_setting(__CONVENTION__, __SUPPRESS__)
    if 'U' in arg_values:
        apply_enforcement_setting(__USAGE__, __USAGE__)
    else:
        apply_enforcement_setting(__USAGE__, __SUPPRESS__)


def main():
    """ main function """
    args = parse_args()
    handle_cli_flags(args)
    exit_code = handle_exit_code(args.pylint_exit_code)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
