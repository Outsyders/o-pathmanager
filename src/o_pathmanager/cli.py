#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from o_pathmanager.factory import PathManagerFactory
from o_pathmanager.config import load_config, _get_show

def main():
    parser = argparse.ArgumentParser(
        description="PathManager CLI using load_config() for defaults+deployment"
    )
    parser.add_argument(
        '--show', dest='show', default=None,
        help='Show name (overrides $SHOW environment variable)'
    )
    parser.add_argument(
        '--os', dest='default_os', choices=['win', 'linux', 'mac'],
        default='linux',
        help='Target OS for generated paths'
    )
    parser.add_argument(
        '--config', '-c', dest='project_config', default="",
        help='Path to a project-specific YAML override; leave empty to load only default+deployment'
    )
    args = parser.parse_args()

    # 1) Determine show name
    show_name = args.show or _get_show() or "VEL"
    if not show_name:
        print("✖ You must supply --show or set the SHOW environment variable", file=sys.stderr)
        sys.exit(1)

    # 2) Load default config
    cfg = load_config()

    # 3) Resolve studio_cfg (handle relative paths inside cfg)
    pkg_dir    = Path(__file__).parent
    raw_studio = Path(cfg.studio_cfg)
    if not raw_studio.is_absolute():
        studio_cfg = pkg_dir / raw_studio
    else:
        studio_cfg = raw_studio
    if not studio_cfg.exists():
        print(f"✖ studio_cfg file not found at {studio_cfg}", file=sys.stderr)
        sys.exit(1)

    # 4) Resolve projects_root from cfg
    projects_root = Path(cfg.projects_root)
    if not projects_root.exists():
        print(f"✖ projects_root folder not found at {projects_root}", file=sys.stderr)
        sys.exit(1)

    # 5) Build the PathManager for this show
    pm = PathManagerFactory.create_for_show(
        studio_cfg=studio_cfg,
        projects_root=projects_root,
        show_name=show_name,
        default_os=args.default_os,
    )

    # 6) Use the manager
    print("Merged Templates:\n")
    for name, conf in pm.get_templates().items():
        print(f"- {name}: {conf}")
    print()

    rep = pm.generate(
        "sg_version_rep",
        {"color": "aces", "resolution": "4K", "ext": "EXR"}
    )
    print("SG Version Rep:", rep)

    ver = pm.generate(
        "sg_version_name",
        {
            "show":           show_name,
            "shotCode":       "shot05",
            "task":           "COMP",
            "sg_version_rep": rep,
            "descriptor":     "FINAL",
            "version":        1
        }
    )
    print("SG Version Name:", ver)

    pub = pm.generate(
        "published_files",
        {
            "root":            "root",
            "seq":             "00",
            "shotCode":        "shot05",
            "task":            "COMP",
            "sg_version_name": ver,
            "ext":             "exr"
        }
    )
    print("Published File:", pub)


if __name__ == '__main__':
    main()
