#!/usr/local/bin/python3
"""
The goal of this script to add a level of customization for exit handling for pylint
"""
from __future__ import print_function

import argparse
import sys
from abc import ABC, abstractmethod

from bitarray import bitarray
from pylint import lint

# Exit values
__FATAL__ = 1
__ERROR__ = 2
__WARNING__ = 4
__REFACTOR__ = 8
__CONVENTION__ = 16
__USAGE__ = 32
__QUALITY__ = 64
__SUPPRESS__ = 0


class BaseHandler(ABC):
    """Base argument handling class"""

    def __init__(self, namespace: argparse.Namespace):
        self._handle_cli_arg(namespace)

    @abstractmethod
    def _handle_cli_arg(self, namespace):
        """Abstract method to be implemented for argument handling"""
        ...


class ExitCodeMutator(BaseHandler):
    """Class for handling pylint exit codes"""
    exit_value_defaults = [
        (__FATAL__, 'fatal message issued', __FATAL__),
        (__ERROR__, 'error message issued', __ERROR__),
        (__WARNING__, 'warning message issued', __WARNING__),
        (__REFACTOR__, 're-factor message issued', __SUPPRESS__),
        (__CONVENTION__, 'convention message issued', __SUPPRESS__),
        (__USAGE__, 'usage error', __USAGE__)
    ]

    def _decode(self, value):
        """Decode the return code value into a bit array.

        Args:
            value(int): Return code from pylint command line.

        Returns:
            list of raised exit codes.

        Example:
            >>> self._decode(1)
            [(1, 'fatal message issued', 1)]
            >>> self._decode(2)
            [(2, 'error message issued', 0)]
            >>> self._decode(3)
            [(1, 'fatal message issued', 1), (2, 'error message issued', 0)]
        """
        return [x[1] for x in zip(bitarray(bin(value)[2:])[::-1], self.exit_value_defaults) if x[0]]

    def _get_messages(self, value):
        """Return a list of raised messages for a given pylint return code.

        Args:
            value(int): Return code from pylint command line.

        Returns:
            list of str: Raised messages.

        Example:
            >>> self._get_messages(1)
            ['fatal message issued']
            >>> self._get_messages(2)
            ['error message issued']
            >>> self._get_messages(3)
            ['fatal message issued', 'error message issued']
        """
        return [x[1] for x in self._decode(value)]

    def _get_exit_code(self, value):
        """Return the exist code that should be returned.

        Args:
            value(int): Return code from pylint command line.

        Returns:
            int: Return code that should be returned when run as a command.

        Example:
            >>> self._get_exit_code(1)
            1
            >>> self._get_exit_code(2)
            2
            >>> self._get_exit_code(3)
            3
            >>> self._get_exit_code(12)
            4
        """
        exit_codes = [x[2] for x in self._decode(value)]
        if not exit_codes:
            return 0
        return sum(exit_codes)

    def handle_exit_code(self, value):
        """
        Exit code handler.

        Takes a pylint exist code as the input parameter, and
        displays all the relevant console messages.

        Args:
            value(int): Return code from pylint command line.

        Returns:
            int: Return code that should be returned when run as a command.

        Example:
            >>> ExitCodeMutator.handle_exit_code(1)
            The following messages were raised:
            <BLANKLINE>
              - fatal message issued
            <BLANKLINE>
            Fatal messages detected.  Failing...
            1
            >>> ExitCodeMutator.handle_exit_code(12)
            The following messages were raised:
            <BLANKLINE>
              - warning message issued
              - refactor message issued
            <BLANKLINE>
            No fatal messages detected.  Exiting gracefully...
            0
        """
        messages = self._get_messages(value)
        exit_code = self._get_exit_code(value)

        if messages:
            print('The following types of issues were found:')
            print('')

            for message in messages:
                print("  - %s" % message)

            print('')

        if exit_code:
            print('The following types of issues are blocking:')
            print('')

            exit_messages = self._get_messages(exit_code)
            for exit_message in exit_messages:
                print("  - %s" % exit_message)

            print('')

        return exit_code

    def _handle_cli_arg(self, namespace):
        """Applies the CLI flags

        Args:
            namespace (argparse.Namespace): namespace from CLI arguments

        """
        if namespace.exit_report:
            arg_value_list = namespace.exit_report.split(',')
            self._set_report_arg_values(arg_value_list)

    def _set_report_arg_values(self, arg_values: []):
        """ Apply an enforcement setting

        Args:
            arg_values (List): A list of setting passed into the '--exit-report' option which can change which exit
            codes will be returned to cli
        """
        if 'F' in arg_values:
            self._apply_enforcement_setting(__FATAL__, __FATAL__)
        else:
            self._apply_enforcement_setting(__FATAL__, __SUPPRESS__)
        if 'E' in arg_values:
            self._apply_enforcement_setting(__ERROR__, __ERROR__)
        else:
            self._apply_enforcement_setting(__ERROR__, __SUPPRESS__)
        if 'W' in arg_values:
            self._apply_enforcement_setting(__WARNING__, __WARNING__)
        else:
            self._apply_enforcement_setting(__WARNING__, __SUPPRESS__)
        if 'R' in arg_values:
            self._apply_enforcement_setting(__REFACTOR__, __REFACTOR__)
        else:
            self._apply_enforcement_setting(__REFACTOR__, __SUPPRESS__)
        if 'C' in arg_values:
            self._apply_enforcement_setting(__CONVENTION__, __CONVENTION__)
        else:
            self._apply_enforcement_setting(__CONVENTION__, __SUPPRESS__)
        if 'U' in arg_values:
            self._apply_enforcement_setting(__USAGE__, __USAGE__)
        else:
            self._apply_enforcement_setting(__USAGE__, __SUPPRESS__)

    def _apply_enforcement_setting(self, key, value):
        """ Apply an enforcement setting

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
        encoded, description, enforce = self.exit_value_defaults[position]
        enforce = value  # set the element to True (error)

        # repack it back into a tuple to match existing data type
        self.exit_value_defaults[position] = encoded, description, enforce


class QualityCheck(BaseHandler):
    """Class for pylint quality check handling"""
    quality_threshold = 0

    def check_quality(self, value):
        """ Check the the given quality is above threshold

        Args:
            value(int): Quality value from pylint command line.

        Returns:
            int: Return code for quality check <b>64</b> for failure and <b>0</b> for pass
        """
        if value < self.quality_threshold:
            print('The code quality is below the minimum acceptable level of ' + str(__QUALITY__))
            return __QUALITY__
        return __SUPPRESS__

    def _handle_cli_arg(self, namespace):
        """
        Applies the CLI flags

        Args:
            namespace (argparse.Namespace): namespace from CLI arguments

        """
        if namespace.quality_gate:
            self.quality_threshold = namespace.quality_gate


def parse_args():
    """Parse command line arguments."""
    desc = "PyLint wrapper that adds option to provides extended exit code handling and quality fail conditions." \
           " All other arguments are passed to pylint.  To see available pylint options run 'pylint -h'."
    parser = argparse.ArgumentParser(description=desc)

    quality_gate_help = 'If the final score is less than the threshold which defaults to 0, 64 will be added to' \
                        ' the resulting exitcode.  pylint quality scores are between 0 to 10, 10 being the best.'
    parser.add_argument('--quality-gate', type=float, metavar='<0.00-10.00>', default=0, help=quality_gate_help)
    suppress_exit_code_help = 'You can choose which issue codes are part of the exit code with this option using' \
                              ' a comma delimited string.  Acceptable values are : F[Fatal], E[Error], W[Warning]' \
                              ', R[Refactor], C[Convention], U[Usage]. Examples:   "-r=R" will report only' \
                              ' Refactor type error codes, "-r=R,C" will report only Refactor and Convention type' \
                              ' error codes.  By default Fatal, Error, Warning and Usage type error codes are' \
                              ' reported'
    parser.add_argument('--exit-report', metavar='<F,E,W,R,C,U>', default='F,E,W,U', help=suppress_exit_code_help)

    args, remaining_args = parser.parse_known_args()

    return args, remaining_args


def main():
    """ main function """
    args, remaining_args = parse_args()
    run = lint.Run(remaining_args, do_exit=False)
    if run:
        ex = ExitCodeMutator(args)
        quality = QualityCheck(args)
        exit_code = ex.handle_exit_code(run.linter.msg_status) + quality.check_quality(run.linter.stats['global_note'])
        if exit_code:
            print('Exiting due to issues...')
        else:
            print('Exiting gracefully...')

        sys.exit(exit_code)


if __name__ == '__main__':
    main()
