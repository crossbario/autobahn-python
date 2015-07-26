from __future__ import absolute_import


def make_logger(logger_type=None):
    if logger_type == "twisted":
        # If we've been asked for the Twisted logger, try and get the new one
        try:
            from twisted.logger import Logger
            return Logger()
        except ImportError:
            pass

    from logging import getLogger
    return getLogger()
