# -*- encoding: utf-8 -*-

from logging import getLogger, INFO, DEBUG, basicConfig
from argparse import ArgumentParser

settings_logger = getLogger('Settings')


class Settings(object):  # pragma: no cover
    """
    This class sets the initial configuration of PartStructuredSpotting, such as activating verbose mode.
    This is not unit-tested, since arguments to parse can't be added to the tests
    """
    def __init__(self):
        self.arg_parser = self.setup_arg_parser()
        self.setup_arg_options()

    @staticmethod
    def setup_arg_parser():
        return ArgumentParser(
            prog='PartStructuredSpotting',
            add_help=True
        )

    def setup_arg_options(self):
        self.add_arguments()
        ArgumentListener(self.arg_parser)

    def add_arguments(self):
        self.arg_parser.add_argument("-v", "--verbose",
                                     help="Activates verbose mode (DEBUG-logging)", action="store_true")


class ArgumentListener(object):  # pragma: no cover
    """
    This class handles the functionality for the given arguments and options via command-line.
    This class is not unit-tested, since the argument parser fails on unittests, since no arguments get passed.
    """
    def __init__(self, arg_parser):
        self.arg_parser = arg_parser
        self.options = self.arg_parser.parse_args()
        self.setup_option_handler()

    def setup_option_handler(self):
        self.setup_verbose_mode()

    def setup_verbose_mode(self):
        debuglevel = INFO
        level_msg = "INACTIVE"
        if self.options.verbose:
            debuglevel = DEBUG
            level_msg = "ACTIVE"

        basicConfig(level=debuglevel)  # , filename=join("..", "pss.log"))
        settings_logger.info("Verbose-Mode %s", level_msg)
