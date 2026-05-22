"""stashpull — Interactive terminal utility to browse, preview,
and selectively restore git stash entries across a repo.
"""

__version__ = "0.1.0"
__all__ = ["stash", "get_version"]


def get_version() -> str:
    """Return the current version string of stashpull.

    Returns
    -------
    str
        The semantic version string (e.g. ``"0.1.0"``).

    Examples
    --------
    >>> from stashpull import get_version
    >>> get_version()
    '0.1.0'
    """
    return __version__
