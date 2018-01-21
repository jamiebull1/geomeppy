"""Utilities for use in geomeppy."""
from typing import Any  # noqa

from six.moves import zip


def almostequal(first, second, places=7):
    # type: (Any, Any, int) -> bool
    """Tests a range of types for near equality."""
    try:
        # try converting to float first
        first = float(first)
        second = float(second)
        # test floats for near-equality
        if round(abs(second - first), places) != 0:
            return False
        else:
            return True
    except ValueError:
        # handle non-float types
        return str(first) == str(second)
    except TypeError:
        # handle iterables
        return all([almostequal(a, b, places) for a, b in zip(first, second)])
