import os


class History:
    def __init__(self):
        self._history = ['']  # contains the whole history
        self._position = 0  # used when navigating through the history
        # this is the end-index of the history, it might be < len(history)-1 if we appended future commands
        self._current = 0

    def load_from_file(self, filename, end=True):
        """
        Loads a file to the history.
        :param filename: File to load
        :param end: Determines whether to put the contents to the end of the history or not
        :return:
        """
        if not os.path.isfile(filename):
            return False
        try:
            with open(filename, 'r') as f:
                hist = map(lambda s: s.rstrip(), f.readlines())
        except IOError as e:
            return e
        # if append to the end, remove current and append afterwards
        current_line = ''
        if end:
            current_line = self._history.pop(self._current)
        self._history.extend(hist)  # append
        if end:
            self._history.append(current_line)
            self._current = len(self._history) - 1
            self._position = self._current
        return True

    def edit(self, line):
        """
        Edits the current line.
        :param line: The new text
        :return:
        """
        self._position = self._current
        self._history[self._current] = line

    def commit(self):
        """
        Saves changes to current line and creates new history entry.
        :return:
        """
        if self._position > self._current:
            # drop empty commands from history
            if len(self._history[self._current].strip()) == 0:
                del self._history[self._current]
            # if we execute a future command, set current to that position
            self._current = self._position
        else:
            # just reset and reuse that entry if empty
            if len(self._history[self._current].strip()) == 0:
                self._position = self._current
                self._history[self._current] = ''
                return
            # otherwise, we have to increment current and reset position
            self._current += 1
            self._position = self._current
        self._history.insert(self._current, '')

    def move_up(self):
        """
        Moves up in the history entries.
        :return: Entry above
        """
        if self._position > 0:
            self._position -= 1
        return self._history[self._position]

    def move_down(self):
        """
        Moves down in the history entries.
        :return: Entry below
        """
        if self._position < len(self._history) - 1:
            self._position += 1
        return self._history[self._position]
