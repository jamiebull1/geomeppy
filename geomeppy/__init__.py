from geomeppy.idf import IDF

# Single source of truth for the package version.
# Bump this value here when releasing a new version; setup.py and the CI
# release workflow (which creates the git tag, GitHub release, and PyPI
# publish) all read it from this file automatically.
__version__ = "0.12.1"

__all__ = ["IDF"]
