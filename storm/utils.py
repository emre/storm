# -*- coding: utf-8 -*-

import os

from termcolor import colored


def fixed_width(text, size):
    text_width = len(text)
    if size > text_width:
        for _ in range(text_width, size):
            text += " "

    return text


COLOR_CODES = [
    "\x1b[1m",
    "\x1b[37m",
    "\x1b[0m",
    "\x1b[32m",
    "\x1b[35m",
]


def get_formatted_message(message, format_type):

    # required for CLI test suite. see tests.py
    if 'TESTMODE' in os.environ and not isinstance(message, ValueError):
        for color_code in COLOR_CODES:
            message = message.replace(color_code, "")

        return "{0} {1}".format(format_type, message)

    format_typed = fixed_width(format_type, 8)
    all_message = ""
    message = " %s" % message

    if format_type == 'error':
        all_message = colored(format_typed, 'white', 'on_red')
    if format_type == 'success':
        all_message = colored(format_typed, 'white', 'on_green')

    return all_message+message