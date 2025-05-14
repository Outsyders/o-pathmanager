from abc import ABC, abstractmethod
from typing import Dict, List, Union

class TransformStrategy(ABC):
    @abstractmethod
    def apply(self, transforms: Dict[str, List[str]], tokens: Dict[str, str]) -> Dict[str, str]:
        pass

class StringTransformerStrategy(TransformStrategy):
    _REGISTRY = {
        'capitalize': str.capitalize,
        'uppercase': str.upper,
        'lowercase': str.lower,
        'padding_format': None, 
        'version_format': None,
    }
    @staticmethod
    def padding_format(value: str) -> str:
        """
        Turn a digit string like "5" into a printf-style "%05d".
        """
        try:
            width = int(value)
        except ValueError:
            raise ValueError(f"Invalid padding '{value}'; must be an integer.")
        return f"%0{width}d"

    _REGISTRY['padding_format'] = padding_format.__func__

    @staticmethod
    def version_format(value: int) -> int:
        """
        Turn "2" into "002", "15" into "015", etc.
        """
        try:
            num = int(value)
        except ValueError:
            raise ValueError(f"Invalid version '{value}'; must be an integer.")
        return f"{num:03d}"
    _REGISTRY['version_format'] = version_format.__func__

    def apply(self,
              transforms: Dict[str, List[str]],
              tokens: Dict[str, str]) -> Dict[str, str]:

        for field, funcs in transforms.items():
            # skip if token missing or explicitly None
            if field not in tokens or tokens[field] is None:
                continue

            # start with its string form
            val = str(tokens[field])

            # apply each named transform in order
            for fn in funcs:
                if fn not in self._REGISTRY:
                    raise KeyError(f"Unknown transform '{fn}' on field '{field}'")
                val = self._REGISTRY[fn](val)

            tokens[field] = val

        return tokens
