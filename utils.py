# March 2018, Lewis Gaul

"""
Utilities.

"""

from functools import partial

# Wrap the built-in print function to not end in a newline and to still
# always print immediately (flush the buffer).
putstr = partial(print, end="", flush=True)
