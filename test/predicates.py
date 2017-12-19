OPEN = {
    '{': '}',
    '[': ']',
    '(': ')',
    '<': '>',
}

CLOSED = {v: k for k, v in OPEN.items()}


def check_balanced(s):
    """Check for balanced parentheses, braces and brackets.

    Args:
        s: The string to be checked.

    Returns:
        True if the {}, [], () and <> brackets are correctly
        balanced and nested. Othewise an exception is raised.

    Raises:
        ValueError: If the brackets are not balanced and correctly
            nested. The exception payload will contain details of
            the problem.
    """
    stack = []
    for i, c in enumerate(s):
        if c in OPEN:
            stack.append((i, c))
        elif c in CLOSED:
            try:
                k, o = stack.pop()
            except IndexError:
                raise ValueError(
                    "Unmatched {c} at index {i} in {s!r}".format(c=c, i=i, s=s))
            if CLOSED[c] != o:
                raise ValueError(
                    "Mismatched {o} at index {k} with {c} at index {i} in {s!r}".format(o=o, k=k, c=c, i=i, s=s))
    if len(stack) != 0:
        raise ValueError(
            "Unmatched {}, in {!r}".format(
                ', '.join("{j} at index {d}".format(j=j, d=d) for d, j in stack),
                s)
        )
    return True
