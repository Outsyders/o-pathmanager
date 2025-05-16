import re
from abc import ABC, abstractmethod
from typing import Dict


class FormatterStrategy(ABC):
    """Interface for all formatter strategies."""

    @abstractmethod
    def format(self, pattern: str, tokens: Dict[str, str]) -> str:
        """Return the formatted string given a pattern and a token map."""
        raise NotImplementedError


class PatternFormatter(FormatterStrategy):
    """
    Default formatter: Python str.format() + separator clean-up.

    The clean-up rules below collapse:
      * multiple underscores        __  → _
      * underscore next to slash    /_  or  _/  → /
      * leading/trailing underscores   _path_/  → path/
      * multiple slashes            //// → /
    """

    _MULTI_UNDER = re.compile(r"_{2,}")        # __ or ___  → _
    _UNDER_SLASH = re.compile(r"/_|_/")        # /_  or  _/ → /
    _EDGE_UNDER  = re.compile(r"^_+|_+$")      # leading or trailing _
    _MULTI_SLASH = re.compile(r"/{2,}")        # //// → /

    def _cleanup(self, path: str) -> str:
        path = self._MULTI_UNDER.sub("_", path)
        path = self._UNDER_SLASH.sub("/", path)
        path = self._EDGE_UNDER.sub("", path)
        path = self._MULTI_SLASH.sub("/", path)
        return path

    # ------------------------------------------------------------------ #
    # FormatterStrategy interface
    # ------------------------------------------------------------------ #

    def format(self, pattern: str, tokens: Dict[str, str]) -> str:
        """
        Fill `pattern` with `tokens`, then normalise separators.

        Example
        -------
        >>> fmt = PatternFormatter()
        >>> pattern = "{root}/{seq}/{shot}_{task}_{descriptor}_v{version}"
        >>> tokens = {
        ...     "root": "/show",
        ...     "seq": "SQ001",
        ...     "shot": "SH010",
        ...     "task": "comp",
        ...     "descriptor": "",      # optional token left empty
        ...     "version": "001",
        ... }
        >>> fmt.format(pattern, tokens)
        '/show/SQ001/SH010_comp_v001'
        """
        filled = pattern.format(**tokens)
        return self._cleanup(filled)