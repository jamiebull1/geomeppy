"""Test for viewing geometry."""
import pytest
from geomeppy.view_geometry import _get_collections
from geomeppy.view_geometry import _get_limits
from tests.conftest import relative_idf
from eppy.iddcurrent import iddcurrent
from geomeppy.idf import IDF
from six import StringIO

x_true = [
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    6.0,
    6.0,
    10.25,
    10.25,
    16.25,
    16.25,
    16.25,
    16.25,
    10.25,
    10.25,
    16.25,
    16.25,
    16.25,
    16.25,
    10.25,
    10.25,
    10.25,
    10.25,
    6.0,
    6.0,
    0.0,
    0.0,
    16.25,
    16.25,
    10.25,
    10.25,
    6.0,
    6.0,
    0.0,
    0.0,
    16.25,
    16.25,
    10.25,
    10.25,
]
y_true = [
    0.0,
    0.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    0.0,
    0.0,
    6.0,
    6.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    6.0,
    6.0,
    0.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    6.0,
    0.0,
    0.0,
    6.0,
    6.0,
    0.0,
    0.0,
    6.0,
]
z_true = [
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    0.0,
    0.0,
    3.0,
    3.0,
    3.0,
    3.0,
    3.0,
    3.0,
    3.0,
    3.0,
    3.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]


def test_abs_coord(relative_idf):
    idf = relative_idf()
    collections = _get_collections(idf)
    x = []
    y = []
    z = []
    for c in collections:
        xdata, ydata, zdata, _ = c._vec
        for x_i, y_i, z_i in zip(xdata, ydata, zdata):
            x.append(x_i)
            y.append(y_i)
            z.append(z_i)
    assert x == x_true
    assert y == y_true
    assert z == z_true

    limits = _get_limits(collections=collections)
    assert limits["x"] == (0.0, 16.25)
    assert limits["y"] == (0.0, 16.25)
    assert limits["z"] == (0.0, 16.25)
