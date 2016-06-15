#!/usr/bin/env python3

import argparse

from curtsies import Input
from ppython.input_handler import InputHandler
from ppython.interpreter import Interpreter
from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.python import Python3Lexer

from ppython.history import History

# parse arguments
parser = argparse.ArgumentParser(description='Interactive Python3 Interpreter.')
parser.add_argument('-a', '--append-history', help='Appends contents of this file to the history.', nargs=1)
args = parser.parse_args()


def hl(txt):
    return highlight(txt, Python3Lexer(), TerminalTrueColorFormatter(style='monokai'))


i = Interpreter()

h = History()
# possibly append history
if args.append_history is not None:
    file = args.append_history[0]
    res = h.load_from_file(file, end=False)
    # errors
    if res is not True:
        if res is False:
            print('Error! Specified file `' + file + '` does not exist')
        else:
            print(res)

ih = InputHandler(h)
ih.set_highlighter(hl)
ih.set_completer(i.complete)
ih.set_prefix('>>> ')
# draw first
ih.draw()


def evaluate(line):
    i.eval(line)
    if i.inblock():
        ih.set_prefix('... ')
        ih.process_input('<TAB>')
    else:
        ih.set_prefix('>>> ')
    ih.draw()


ih.register_handler('<Ctrl-j>', evaluate)

with Input(keynames='curtsies', sigint_event=True) as input_generator:
    for c in input_generator:
        out = ih.process_input(c)
        if out is False:
            break
