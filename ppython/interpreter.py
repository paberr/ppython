import re
import traceback


class Interpreter:
    def __init__(self):
        self._inblock = False
        self._last_empty = False
        self._aggregate = []
        self._environment = dict()
        self.comments = re.compile(r'#.*$', re.MULTILINE)
        self.identifier = re.compile(r'(?:^|\s)((?:[^\d\W]\w*\.)*(?:[^\d\W]\w*))$')
        # blockopeners are :({[ and """,'''
        # currently, we find them by explicitly looking for compilation errors
        # TODO: find better way to do this
        self.blockopeners = (
            'EOF while scanning triple-quoted string literal',
            'unexpected EOF while parsing'
        )

    def inblock(self):
        """
        Returns whether a block is open currently.
        :return: True if a block is open
        """
        return self._inblock

    def eval(self, line):
        """
        Evaluates line, looks for blocks and eventually executes statements...
        :param line: Line to be fed
        :return:
        """
        stripped_line = self._strip(line)
        if len(stripped_line) == 0:
            # leave block if:
            # - line completely empty
            # - or two empty tab lines
            if self._inblock:
                only_spaces = len(line.strip()) == 0
                # if block is left, execute aggregation
                # leave if line empty or last empty and only spaces
                if len(line) == 0 or (self._last_empty and only_spaces):
                    code = '\n'.join(self._aggregate)
                    compilation = self._try_compile(code)
                    if compilation is False:
                        return
                    self._aggregate = []
                    self._inblock = False
                    self._last_empty = False
                    self._exec(compilation)
                elif only_spaces:
                    # only spaces, so we need two such lines
                    self._last_empty = True
                else:
                    self._last_empty = False
            return  # if empty line


        if not self._inblock:
            compilation = self._try_compile(line)

        self._last_empty = False
        if self._inblock:
            self._aggregate.append(line)
        else:
            self._exec(compilation)

    def _try_compile(self, line):
        try:
            return compile(line, '<input>', 'single')
        except SyntaxError as e:
            if e.msg in self.blockopeners:
                self._inblock = True
            else:
                traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
        return False

    def _exec(self, compilation):
        """
        Executes some code and catches exceptions.
        :param code: Code to execute
        :return:
        """
        try:
            exec(compilation, self._environment)
        except Exception as e:
            traceback.print_exc()

    def _strip(self, line):
        """
        Strips away comments and spaces.
        :param line: The line to strip
        :return: The stripped line
        """
        return self.comments.sub('', line).strip()

    def complete(self, line):
        """
        A preliminary auto complete function.
        Only works for things in the global environment, so far!
        And only up to a depth of 1.
        :param line: the current line
        :return: completion in case of success, False otherwise
        """
        match = self.identifier.search(line)
        if match is not None:
            parts = match.group(1).split('.')
            environ = self._environment

            if len(parts) > 0:
                last_part =  parts[-1]

                # submodules
                if len(parts) > 1:
                    if parts[-2] not in environ:
                        return False
                    environ = dir(environ[parts[-2]]) # update environ

                matches = [key for key in environ if key.startswith(last_part)]

                if len(matches) == 1:
                    return matches[0][len(last_part):]
        return False