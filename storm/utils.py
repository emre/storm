# -*- coding: utf-8 -*-

from termcolor import colored


def fixed_width(text, size):
    text_width = len(text)
    if size > text_width:
        for _ in range(text_width, size):
            text += " "

    return text


def get_formatted_message(message, format_type):
    format_typed = fixed_width(format_type, 8)
    all_message = ""
    message = " %s" % message

    if format_type == 'error':
        all_message = colored(format_typed, 'white', 'on_red')
    if format_type == 'success':
        all_message = colored(format_typed, 'white', 'on_green')

    return all_message+message