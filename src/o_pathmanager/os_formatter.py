# pathmanager/os_formatter.py

from abc import ABC, abstractmethod
from pathlib import PureWindowsPath, PurePosixPath
from typing import Union

class OSPathStrategy(ABC):
    @abstractmethod
    def make_path(self, os_name: str, filled: str) -> Union[str, PureWindowsPath, PurePosixPath]:
        """Convert a POSIX‐style filled pattern into an OS‐specific path string."""
        pass

class OSPathFormatter(OSPathStrategy):
    def make_path(self, os_name: str, filled: str) -> Union[PureWindowsPath, PurePosixPath]:
        key = os_name.strip().lower()
        parts = filled.split('/')
        if key == 'win':
            return PureWindowsPath(*parts)
        if key in ('linux', 'mac'):
            return PurePosixPath(*parts)
        raise ValueError(f"Unknown OS '{os_name}'")
