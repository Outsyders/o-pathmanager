from abc import ABC, abstractmethod
from pathlib import PureWindowsPath, PurePosixPath
from typing import Dict

class FormatterStrategy(ABC):
    @abstractmethod
    def format(self, pattern: str, tokens: Dict[str, str]) -> str:
        pass

class PatternFormatter(FormatterStrategy):
    def format(self, pattern, tokens):
        return pattern.format(**tokens)

