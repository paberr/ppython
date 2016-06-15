import os


class History:
    def __init__(self):
        self.history = ['']
        self.position = 0
        self.current = 0

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
            current_line = self.history.pop(self.current)
        self.history.extend(hist) # append
        if end:
            self.history.append(current_line)
            self.current = len(self.history) - 1
            self.position = self.current
        return True

    def edit(self, line):
        """
        Edits the current line.
        :param line: The new text
        :return:
        """
        self.position = self.current
        self.history[self.current] = line

    def commit(self):
        """
        Saves changes to current line and creates new history entry.
        :return:
        """
        if self.position > self.current:
            del self.history[self.current]
            self.current = self.position
        else:
            self.current += 1
            self.position = self.current
        self.history.insert(self.current, '')

    def move_up(self):
        """
        Moves up in the history entries.
        :return: Entry above
        """
        if self.position > 0:
            self.position -= 1
        return self.history[self.position]

    def move_down(self):
        """
        Moves down in the history entries.
        :return: Entry below
        """
        if self.position < len(self.history) - 1:
            self.position += 1
        return self.history[self.position]


