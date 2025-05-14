# pathmanager/loader.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict
import yaml
import copy

class TemplateLoaderStrategy(ABC):
    @abstractmethod
    def load(self, config_paths: List[Path]) -> Dict[str, dict]:
        """Load and merge template definitions."""
        pass

class YamlDeepMergeLoader(TemplateLoaderStrategy):
    def load(self, config_paths: List[Path]) -> Dict[str, dict]:
        templates: Dict[str, dict] = {}

        for path in config_paths:
            print(f"[DEBUG] Attempting to load config: {path}")
            if not path.exists():
                print(f"[WARNING] Config file '{path}' not found, skipping.")
                continue

            try:
                data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
            except Exception as e:
                print(f"[ERROR] Failed to parse YAML at {path}: {e}")
                continue

            section = data.get('templates', {})
            print(f"[DEBUG] Parsed templates at {path}: {section}")

            for name, conf in section.items():
                if name not in templates:
                    templates[name] = copy.deepcopy(conf)
                else:
                    # merge transforms
                    existing = templates[name].get('transforms', {})
                    override = conf.get('transforms', {})
                    merged = {k: v[:] for k, v in existing.items()}
                    for field, funcs in override.items():
                        merged.setdefault(field, []).extend(funcs)
                    templates[name]['transforms'] = merged

                    # merge other keys
                    for k, v in conf.items():
                        if k == 'transforms': 
                            continue
                        if isinstance(v, dict) and isinstance(templates[name].get(k), dict):
                            self._deep_merge(templates[name][k], v)
                        else:
                            templates[name][k] = copy.deepcopy(v)

        print(f"[DEBUG] Final merged templates: {templates}")
        return templates

    def _deep_merge(self, base: dict, override: dict) -> None:
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                self._deep_merge(base[key], val)
            else:
                base[key] = copy.deepcopy(val)
