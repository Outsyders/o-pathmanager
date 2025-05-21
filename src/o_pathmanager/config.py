from pathlib import Path
import yaml
import os
from typing import Dict, Optional, Any

class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert nested dictionaries to DotDict
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, key: str) -> Any:
        if key not in self:
            raise AttributeError(f"Config has no attribute '{key}'")
        return self[key]
    
    def __setattr__(self, key: str, value: Any) -> None:
        # Convert dictionary to DotDict when assigning
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        self[key] = value

def _get_show() -> Optional[str]:
    return os.getenv('SHOW')

def _get_deployment_type() -> Optional[str]:
    return os.getenv('USE_DEPLOYMENTS')

def _find_project_config() -> Optional[Path]:
    show = _get_show()
    if not show:
        return None
        
    deployment_type = _get_deployment_type()
    config_file = f'default-{deployment_type}.yaml' if deployment_type else 'default.yaml'
    possible_paths = [
        Path('/mnt/o/projects') / show / f'configs/o-pathmanager/{config_file}',
        Path('O:/projects') / show / f'configs/o-pathmanager/{config_file}'
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def load_config(project_config: str = None) -> DotDict:
    # Always load default config first
    default_config_path = Path(__file__).parent / 'config' / 'default.yaml'
    # Get top level package name

    print(f"Loading default config from: {default_config_path}")
    if not default_config_path.exists():
        raise FileNotFoundError(f"Default config not found at {default_config_path}")
    
    with default_config_path.open('r') as f:
        config = _convert_to_dot_dict(yaml.safe_load(f) or {})
        config['default_config_path'] = str(default_config_path)
    
    # Load deployment-specific config if environment variable is set
    deployment_type = _get_deployment_type()
    if deployment_type:
        deployment_config_path = Path(__file__).parent / 'config' / f'default-{deployment_type}.yaml'
        if deployment_config_path.exists():
            print(f"Loading {deployment_type} overrides from: {deployment_config_path}")
            with deployment_config_path.open('r') as f:
                deployment_settings = yaml.safe_load(f) or {}
                _deep_update(config, deployment_settings)
        else:
            print(f"Deployment config not found at: {deployment_config_path}")

    # Try to load project config if not explicitly provided
    if project_config is None:
        project_config = _find_project_config()
    
    # Override with project config if available
    if project_config:
        project_path = Path(project_config)
        if project_path.exists():
            print(f"Loading project config from: {project_path}")
            with project_path.open('r') as f:
                project_settings = yaml.safe_load(f) or {}
                _deep_update(config, project_settings)
        else:
            print(f"Project config not found at: {project_path}")
    
    return config

def _convert_to_dot_dict(d: Dict) -> DotDict:
    result = DotDict()
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = _convert_to_dot_dict(value)
        else:
            result[key] = value
    return result

def _deep_update(base_dict: DotDict, update_dict: Dict) -> None:
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = _convert_to_dot_dict(value) if isinstance(value, dict) else value