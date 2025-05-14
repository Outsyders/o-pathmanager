# manager.py
from pathlib import Path
import copy
from .loader        import TemplateLoaderStrategy, YamlDeepMergeLoader
from .transformer   import TransformStrategy, StringTransformerStrategy
from .validator     import ValidationStrategy, TokenValidatorStrategy
from .formatter     import PatternFormatter
from .os_formatter  import OSPathFormatter

class PathManager:
    def __init__(self,
                 config_paths,
                 default_os=None,
                 loader: TemplateLoaderStrategy = None,
                 transformer: TransformStrategy = None,
                 validator: ValidationStrategy = None,
                 formatter: PatternFormatter = None,
                 os_formatter: OSPathFormatter = None):
        # Validate config_paths
        if not config_paths:
            raise ValueError("config_paths cannot be empty.")
        for path in config_paths:
            if path is None:
                raise ValueError("One of the config paths is None.")
            if not isinstance(path, Path):
                raise TypeError(f"Expected Path object, got {type(path)}: {path}")
            if not path.exists():
                raise FileNotFoundError(f"Config path does not exist: {path}")

        self._default_os   = default_os
        self._loader       = loader       or YamlDeepMergeLoader()
        self._transformer  = transformer  or StringTransformerStrategy()
        self._validator    = validator    or TokenValidatorStrategy()
        self._formatter    = formatter    or PatternFormatter()
        self._os_formatter = os_formatter or OSPathFormatter()
        self._templates    = self._loader.load(config_paths)

    def get_templates(self):
        """Expose the raw templates dict so callers can introspect."""
        return self._templates

    def generate(self, name, tokens, os_name=None):
        if name not in self._templates:
            raise KeyError(f"No template '{name}'")
        tpl = copy.deepcopy(self._templates[name])

        # 1) Required tokens
        for req in tpl.get('required_tokens', []):
            if req not in tokens:
                raise KeyError(f"Missing required token '{req}' for template '{name}'")

        # 2) Optional tokens exist (even if empty)
        for opt in tpl.get('optional_tokens', []):
            tokens.setdefault(opt, '')

        # 3) Inject default_tokens and auto-format any integer defaults as "%0Nd"
        for key, val in tpl.get('default_tokens', {}).items():
            # only set if caller didn’t provide or provided empty
            if key not in tokens or tokens[key] in (None, ''):
                tokens[key] = val
            # if it’s an integer default, convert to "%0Nd" string
            if isinstance(tokens[key], int):
                tokens[key] = f"%0{tokens[key]}d"

        # 4) Apply all other string transforms (lowercase, uppercase, etc.)
        tokens = self._transformer.apply(tpl.get('transforms', {}), tokens)

        # 5) Special‐case eye mapping
        eye = tokens.get('eye')
        if eye in ('l', 'r'):
            tokens['eye'] = '%v'
        elif eye in ('left', 'right'):
            tokens['eye'] = '%V'
        # (If eye was empty or something else, we leave it as-is.)

        # 6) Validate final tokens
        self._validator.validate(name, tokens, tpl)

        # 7) Interpolate into pattern and return Path / OS-specific path
        filled = self._formatter.format(tpl['pattern'], tokens)
        target = os_name or self._default_os
        if target:
            return self._os_formatter.make_path(target, filled)
        return Path(filled)
