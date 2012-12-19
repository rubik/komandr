# -*- coding: utf-8 -*-
"""Simple module helps you convert your oridnary functions into cool command-line interfaces
using :py:module:``argparse`` in backyard.

"""
import sys
import inspect
import argparse
from itertools import izip_longest


class prog(object):
    """Class to hold an isolated command registry and execution blocks to keep
    them within the same namespace.

    """
    _COMMAND_FLAG = '_command'
    _POSITIONAL = type('_positional', (object,), {})

    def __init__(self, version='0.0.1', **kwargs):
        """Constructor

        :param version: program version
        :param type: str

        :param **kwargs: keyword arguments those passed through to
                         :py:class:``argparse.ArgumentParser`` constructor
        :param type: dict

        """
        self.parser = argparse.ArgumentParser(**kwargs)
        self.parser.add_argument('-v', '--version', action='version',
                                 version=version)
        self.subparsers = self.parser.add_subparsers()

    def command(self, func):
        """Convenient decorator function which simply registers a function into
        command registry.

        :param func: command function
        :param type: function

        """
        return self._generate_command(func)

    def _generate_command(self, func):
        """Generates a command parser for given func.

        :param func: func to generate related command parser
        :param type: function

        """
        subparser = self.subparsers.add_parser(func.__name__)
        spec = inspect.getargspec(func)
        opts = reversed(list(izip_longest(reversed(spec.args or []),
                                          reversed(spec.defaults or []),
                                          fillvalue=self._POSITIONAL())))
        for k, v in opts:
            is_positional = isinstance(v, self._POSITIONAL)
            arg_name = k if is_positional else '--%s' % k
            arg = subparser.add_argument(arg_name)
            arg.required = v is None
            arg.default = v
        subparser.set_defaults(**{self._COMMAND_FLAG: func})
        return func

    def execute(self, arg_list):
        """Main function to parse and dispatch commands by given arg_list after
        generating corresponding parser for each one.

        :param arg_list: all arguments provided by the command line
        :param type: list

        """
        arg_map = self.parser.parse_args(arg_list).__dict__
        command = arg_map.pop(self._COMMAND_FLAG)
        return command(**arg_map)

    def __call__(self):
        """Calls :py:func:``execute`` with :py:class:``sys.argv`` excluding
        executing script name arg which comes as first one.

        """
        self.execute(sys.argv[1:])

main = prog()
command = main.command
execute = main.execute
