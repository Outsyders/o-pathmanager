# factory.py
from pathlib import Path
from typing import Optional

from .manager import PathManager
from .loader import YamlDeepMergeLoader
from .transformer import StringTransformerStrategy
from .validator import TokenValidatorStrategy
from .formatter import PatternFormatter
from .os_formatter import OSPathFormatter

class PathManagerFactory:

    @staticmethod
    def create_for_project(
        studio_cfg: Path,
        override_cfg: Optional[Path] = None,
        default_os=None
    ) -> PathManager:
        """
        Build a PathManager from one or two YAMLs.
        If override_cfg is None, only the studio_cfg is loaded.
        """
        config_paths = [studio_cfg]
        if override_cfg:
            config_paths.append(override_cfg)

        return PathManager(
            config_paths,
            default_os,
            loader=YamlDeepMergeLoader(),
            transformer=StringTransformerStrategy(),
            validator=TokenValidatorStrategy(),
            formatter=PatternFormatter(),
            os_formatter=OSPathFormatter(),
        )

    @staticmethod
    def create_for_show(
        studio_cfg: Path,
        projects_root: Path,
        show_name: str,
        default_os=None
    ) -> PathManager:
        """
        Look for overrides.yaml under projects_root/show_name/configs.
        If found, merge it; otherwise just use the studio_cfg.
        """
        if not projects_root:
            raise ValueError("projects_root cannot be None.")

        over = projects_root / show_name / 'configs' / 'overrides.yaml'
        print(f"[DEBUG] studio_cfg: {studio_cfg}")
        print(f"[DEBUG] overrides path: {over}")

        if not studio_cfg.exists():
            raise ValueError(f"Invalid studio_cfg: {studio_cfg}")

        if over.exists():
            # merge default + project overrides
            return PathManagerFactory.create_for_project(
                studio_cfg, over, default_os
            )
        else:
            # no overrides file → just load the studio config
            return PathManagerFactory.create_for_project(
                studio_cfg, None, default_os
            )
