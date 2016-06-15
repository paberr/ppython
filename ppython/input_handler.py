import curtsies.events as ev
import sys

DELIMITERS = ' .'


def print_console(txt, length=None, newline=False):
    """
    Prints txt without newline, cursor positioned at the end.
    :param txt: The text to print
    :param length: The txt will be padded with spaces to fit this length
    :param newline: If True, a newline character will be appended
    :return:
    """
    if length is None:
        length = len(txt)
    sys.stdout.write('\r{{: <{}}}'.format(length).format(txt))
    if newline:
        sys.stdout.write('\n')
    sys.stdout.flush()


def move_next_line():
    sys.stdout.write('\n')
    sys.stdout.flush()


def find_next_in_list(lst, what, start=0, reverse=False):
    """
    Finds the next occurrence of what in lst starting at start.
    :param lst: The list to search
    :param what: The item to find, should be an iterable
    :param start: The starting position in the list
    :param reverse: Set this to True in order to traverse the list towards 0
    :return: False if no occurrence found, index otherwise
    """
    if start < 0 or start >= len(lst):
        return False

    end = -1 if reverse else len(lst)
    step = -1 if reverse else 1

    for i in range(start, end, step):
        if lst[i] in what:
            return i
    return False


class InputHandler:
    def __init__(self, history):
        self._input = []
        self._position = 0
        self._handlers = {}
        self._highlight = None
        self._max_length = 0
        self._complete = None
        self._history = history
        self._prefix = ''

    def process_input(self, c):
        """
        Processes the input captured by curtsies.
        :param c: the input, either a curtsies keystroke or an event
        :return: False if program should stop, the current line otherwise
        """
        if isinstance(c, ev.Event):
            return self._process_event(c)
        else:
            return self._process_char(c)

    def register_handler(self, key, handler):
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(handler)

    def set_highlighter(self, highlight):
        self._highlight = highlight

    def set_completer(self, complete):
        self._complete = complete

    def set_prefix(self, prefix):
        self._prefix = prefix

    def _process_char(self, c):
        """
        Processes keystrokes internally, may call handlers as well.
        :param c: The curtsies keystroke
        :return: The current line
        """
        if len(c) == 1:
            self._insert(c)
        elif c == '<LEFT>':
            self._left()
        elif c == '<RIGHT>':
            self._right()
        elif c == '<UP>':
            self._hist_up()
        elif c == '<DOWN>':
            self._hist_down()
        elif c == '<SPACE>':
            self._insert(' ')
        elif c == '<TAB>':
            if not self._tab_completion():
                self._insert('    ')
        elif c == '<BACKSPACE>':
            self._back()
        elif c == '<Ctrl-w>':
            self._delete_last_word()
        elif c == '<DELETE>':
            self._delete()
        elif c == '<HOME>' or c == '<Ctrl-a>':
            self._home()
        elif c == '<END>' or c == '<Ctrl-e>':
            self._end()
        elif c == '<Ctrl-u>':
            self._delete_before()
        elif c == '<Ctrl-k>':
            self._delete_after()
        elif c == '<Esc+f>':
            self._move_word_forwards()
        elif c == '<Esc+b>':
            self._move_word_backwards()
        elif c == '<Ctrl-r>':
            pass # history search mode
        elif c == '<ESC>':
            pass # history search mode
        elif c == '<Ctrl-j>':
            old_line = self._newline()
            if c in self._handlers:
                for handler in self._handlers[c]:
                    handler(old_line)
        elif c == '<Ctrl-c>' or c == '<Ctrl-d>':
            return False

        # new lines are handled differently
        if c in self._handlers and c != '<Ctrl-j>':
            # call handlers if necessary
            for handler in self._handlers[c]:
                handler(self._curline())

        return self._curline()

    def _process_event(self, e):
        """
        Processes events internally.
        :param e: The event
        :return: False in case of SigInt, the input otherwise
        """
        if isinstance(e, ev.SigIntEvent):
            return False
        elif isinstance(e, ev.PasteEvent):
            for c in e.events:
                self.process_input(c)
        return self._curline()

    def _line_changed(self):
        self._history.edit(self._curline())

    def _hist_up(self):
        """
        Moves up in the history object.
        :return:
        """
        self._input = list(self._history.move_up())
        self._position = len(self._input)
        self._max_length = max(self._max_length, len(self._input))
        self.draw()

    def _hist_down(self):
        """
        Moves down in the history object.
        :return:
        """
        self._input = list(self._history.move_down())
        self._position = len(self._input)
        self._max_length = max(self._max_length, len(self._input))
        self.draw()

    def _curline(self):
        """
        Returns the current line.
        :return: current line
        """
        return ''.join(self._input)

    def _insert(self, c):
        """
        Inserts a character at current position, moves cursor forward and redraws.
        :param c: character
        :return:
        """
        if len(c) > 1:
            # only insert single characters
            for cc in c:
                self._insert(cc)
            return
        self._input.insert(self._position, c)
        self._position += 1
        self._max_length = max(self._max_length, len(self._curline()))  # we need this for drawing
        self._line_changed()
        self.draw()

    def _left(self):
        """
        Moves cursor back and redraws.
        :return:
        """
        if self._position > 0:
            self._position -= 1
            self.draw()

    def _home(self):
        """
        Moves cursor home and redraws.
        :return:
        """
        self._position = 0
        self.draw()

    def _right(self):
        """
        Moves cursor forward and redraws.
        :return:
        """
        if self._position < len(self._input):
            self._position += 1
            self.draw()

    def _end(self):
        """
        Moves cursor to end and redraws.
        :return:
        """
        self._position = len(self._input)
        self.draw()

    def _move_word_forwards(self):
        """
        Moves cursor towards the next delimiter.
        :return:
        """
        next_del = find_next_in_list(self._input, DELIMITERS, start=self._position+1)
        if next_del is False:
            self._end()
        else:
            self._position = next_del
            self.draw()

    def _move_word_backwards(self):
        """
        Moves cursor towards the next delimiter.
        :return:
        """
        next_del = find_next_in_list(self._input, DELIMITERS, start=self._position-2, reverse=True)
        if next_del is False:
            self._home()
        else:
            self._position = next_del + 1
            self.draw()

    def _delete_last_word(self):
        """
        Deletes until last delimiter.
        :return:
        """
        next_del = find_next_in_list(self._input, DELIMITERS, start=self._position - 2, reverse=True)
        if next_del is False:
            next_del = 0
        else:
            next_del += 1

        del self._input[next_del:self._position]

        self._position = next_del
        self._line_changed()
        self.draw()

    def _back(self):
        """
        Removes element in front of cursor, moves cursor back and redraws.
        :return:
        """
        if self._position > 0:
            del self._input[self._position - 1]
            self._position -= 1
            self._line_changed()
            self.draw()

    def _delete(self):
        """
        Removes element behind cursor and redraws.
        :return:
        """
        if self._position < len(self._input):
            del self._input[self._position]
            self._line_changed()
            self.draw()

    def _delete_before(self):
        """
        Deletes everything in front of the cursor.
        :return:
        """
        self._input = self._input[self._position:]
        self._position = 0
        self._line_changed()
        self.draw()

    def _delete_after(self):
        """
        Deletes everything after the cursor.
        :return:
        """
        self._input = self._input[:self._position]
        self._line_changed()
        self.draw()

    def _newline(self):
        """
        Creates a new line and returns the old one.
        :return: old line
        """
        self._history.commit()
        old_line = self._curline()
        self._position = 0
        self._max_length = 0
        self._input = []
        move_next_line()
        return old_line

    def draw(self):
        """
        Draws input with cursor at right position.
        :return:
        """
        whole_line = self._curline()
        cursor_line = whole_line[:self._position]
        # add prefix
        whole_line = self._prefix + whole_line
        cursor_line = self._prefix + cursor_line
        # highlight texts
        if self._highlight is not None:
            whole_line_h = self._highlight(whole_line).strip()
            self._max_length = max(len(whole_line_h), self._max_length)
            cursor_line_h = self._highlight(cursor_line).strip()
        else:
            whole_line_h = whole_line
            cursor_line_h = cursor_line
        # first print whole line
        print_console(whole_line_h, self._max_length)
        # then print for cursor position
        print_console(cursor_line_h, len(cursor_line))

    def _tab_completion(self):
        """
        Calls completion function. If possible insert completion.
        :return: True if completion was successful
        """
        if self._complete is not None:
            # try completing
            completion = self._complete(self._curline()[:self._position])
            if completion is not False:
                # if successful, insert the completion
                for c in completion:
                    self._insert(c)
                return True
        return False

