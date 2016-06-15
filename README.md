# ppython
An interactive python3 interpreter with pretty syntax highlighting. Also allows to preload history files.
More specifically, it is based on `pygments` using the monokai theme.
The interpreter can be configured to load a set of "future" statements from a file.
You can then use the arrow keys to navigate through these statements.

This is especially useful for presenting or teaching something python related.
Just provide a file with all statements you would like to cover and then use ppython to navigate through the list.
Moreover, you can execute own statements at any point in time interactively.

# How to run the interpreter
Currently, the easiest way to run the interpreter is:

1. Cloning the repository.
2. Change into the repository directory and run:
`python3 -m ppython`

Options are available using:
`python3 -m ppython -h`

To preload a history, use the `-a FILENAME` argument.