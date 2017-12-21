class AlwaysEqual:

    def __eq__(self, rhs):
        return True

    def __ne__(self, rhs):
        return False

    def __le__(self, rhs):
        return True

    def __ge__(self, rhs):
        return True

    def __lt__(self, rhs):
        return False

    def __gt__(self, rhs):
        return False