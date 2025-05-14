from pathlib import Path
from .manager import PathManager
from .loader import YamlDeepMergeLoader
from .transformer import StringTransformerStrategy
from .validator import TokenValidatorStrategy
from .formatter import PatternFormatter
from .os_formatter import OSPathFormatter

class PathManagerFactory:
    @staticmethod
    def create_for_project(studio_cfg: Path, override_cfg: Path, default_os=None) -> PathManager:
        return PathManager(
            [studio_cfg, override_cfg],
            default_os,
            loader=YamlDeepMergeLoader(),
            transformer=StringTransformerStrategy(),
            validator=TokenValidatorStrategy(),
            formatter=PatternFormatter(),
            os_formatter=OSPathFormatter(),
        )

    @staticmethod
    def create_for_show(studio_cfg: Path, projects_root: Path, show_name: str, default_os=None) -> PathManager:
        over = projects_root / show_name / 'configs' / 'overrides.yaml'
        return PathManagerFactory.create_for_project(studio_cfg, over, default_os)
