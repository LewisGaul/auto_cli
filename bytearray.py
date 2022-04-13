# March 2018, Lewis Gaul

"""
Wrap builtin bytearray.

"""

from functools import wraps


def use_str(method, self):
    @wraps(method)
    def new_method(*args, **kwargs):
        return getattr(str(self), method.__name__)(*args, **kwargs)

    return new_method


class Buffer(bytearray):
    def __init__(self, s=""):
        if isinstance(s, str):
            s = s.encode()
        super().__init__(s)
        # First convert most string methods to use strings directly.
        for method in [
            "capitalize",
            "center",
            "count",
            "endswith",
            "expandtabs",
            "find",
            "index",
            "join",
            "ljust",
            "lower",
            "lstrip",
            "partition",
            "replace",
            "rfind",
            "rindex",
            "rjust",
            "rpartition",
            "rsplit",
            "rstrip",
            "split",
            "splitlines",
            "startswith",
            "swapcase",
            "title",
            "translate",
            "upper",
            "zfill",
        ]:
            setattr(self, method, use_str(getattr(str, method), self))

    def __repr__(self):
        return "Buffer({})".format(str(self))

    def __str__(self):
        return str(bytes(self))[2:-1]

    def __contains__(self, s):
        if isinstance(s, str):
            s = s.encode()
        return super().__contains__(s)

    def __getitem__(self, i):
        return str(self)[i]

    def __eq__(self, s):
        return str(self) == s

    # Methods which alter self.
    def __iadd__(self, s):
        """
        Allow adding of strings or iterables of integers, using the extend
        method. Also print the added string in the correct position.
        """
        if (
            hasattr(s, "__iter__") and not all([isinstance(c, int) for c in s])
        ) and not isinstance(s, str):
            raise TypeError("a string or iterable of integers is required")
        if isinstance(s, str):
            self.extend(s.encode())
        else:
            self.extend(s)

        return self

    def append(self, c):
        if isinstance(c, (str, bytes)) and len(c) == 1:
            c = ord(c)
        super().append(c)

    def extend(self, s):
        if isinstance(s, str):
            s = s.encode()
        super().extend(s)

    def insert(self, i, c):
        if isinstance(c, (str, bytes)) and len(c) == 1:
            c = ord(c)
        super().insert(i, c)

    def pop(self, index=-1):
        return chr(super().pop(index))

    def remove(self, c):
        if isinstance(c, (str, bytes)) and len(c) == 1:
            c = ord(c)
        super().remove(c)

    def strip(self, leave_trailing_space=False):
        """
        Strip out unnecessary spaces - leaves a single space anywhere there was
        at least one space before except at the start.
        """
        s = " ".join(self.split())
        if str(self).strip() and self[-1] == " " and leave_trailing_space:
            s += " "
        self.set(s)

    def stripped(self, end_only=True):
        """
        Strip whitespace - returns a string and makes no changes in-place,
        in a similar manner to 'sorted' rather than 'sort'. 
        """
        if end_only:
            return ("a" + str(self)).strip()[1:]
        else:
            return str(self).strip()

    def set(self, s):
        self.clear()
        self.extend(s)
