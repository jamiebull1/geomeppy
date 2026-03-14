from geomeppy.idf import IDF

# Single source of truth for the package version.
# Bump this value here AND in pyproject.toml when releasing a new version.
# The CI release workflow reads this value to create the git tag, GitHub
# release, and PyPI publish.
__version__ = "0.12.2"

__all__ = ["IDF"]
