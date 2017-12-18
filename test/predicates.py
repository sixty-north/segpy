OPEN = {
    '{': '}',
    '[': ']',
    '(': ')',
    '<': '>',
}

CLOSED = {v: k for k, v in OPEN.items()}

def check_balanced(s):
    """Check for balanced parentheses, braces and brackets."""
    stack = []
    for i, c in enumerate(s):
        if c in OPEN:
            stack.append((i, c))
        elif c in CLOSED:
            try:
                k, o = stack.pop()
            except IndexError:
                raise ValueError(
                    f"Unmatched {c} at index {i} in {s!r}")
            if CLOSED[c] != o:
                raise ValueError(
                    f"Mismatched {o} at index {k} with {c} at index {i} in {s!r}")
    if len(stack) != 0:
        raise ValueError(
            "Unmatched {}, in {!r}".format(
            ', '.join(f"{j} at index {d}" for d, j in stack),
            s)
        )
    return True

