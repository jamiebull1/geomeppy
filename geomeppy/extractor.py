"""Module for extracting the geometry from an existing IDF.

There is the option to copy:

- thermal zone description and geometry
- surface construction elements

"""
import itertools
from typing import Optional  # noqa

from .idf import EpBunch, Idf_MSequence, IDF, new_idf  # noqa


def copy_constructions(source_idf, target_idf=None, fname=None):
    # type: (IDF, Optional[IDF], str) -> IDF
    """Extract construction objects from a source IDF and add them to a target IDF or a new IDF.

    :param source_idf: An IDF to source objects from.
    :param target_idf: An optional IDF to add objects to. If none is passed, a new IDF is returned.
    :param fname: A name for the new IDF created if no target IDF is passed in.
    :returns: Either the target IDF or a new IDF containing the construction objects.
    """
    group = 'Surface Construction Elements'
    if not target_idf:
        target_idf = new_idf(fname)
    idf = copy_group(source_idf, target_idf, group)
    return idf


def copy_geometry(source_idf, target_idf=None, fname=None):
    # type: (IDF, Optional[IDF], str) -> IDF
    """Extract geometry objects from a source IDF and add them to a target IDF or a new IDF..

    :param source_idf: An IDF to source objects from.
    :param target_idf: An optional IDF to add objects to. If none is passed, a new IDF is returned.
    :param fname: A name for the new IDF created if no target IDF is passed in.
    :returns: Either the target IDF or a new IDF containing the geometry objects.
    """
    group = 'Thermal Zones and Surfaces'
    if not target_idf:
        target_idf = new_idf(fname)
    idf = copy_group(source_idf, target_idf, group)
    return idf


def copy_group(source_idf, target_idf, group):
    # type: (IDF, IDF, str) -> IDF
    """Extract a group of objects from a source IDF and add them to a target IDF.

    :param source_idf: An IDF to source objects from.
    :param target_idf: An IDF to add objects to.
    :param group: The name of the group of objects to copy.
    :returns: A new IDF containing the objects which belong to the group.
    """
    keys = source_idf.getiddgroupdict()[group]
    objects = [source_idf.idfobjects[key.upper()] for key in keys]
    for obj in itertools.chain(*objects):
        target_idf.copyidfobject(obj)
    return target_idf
