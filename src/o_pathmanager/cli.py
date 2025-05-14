#!/usr/bin/env python3
import argparse
from pathlib import Path
from o_pathmanager.factory import PathManagerFactory

def main():
    parser = argparse.ArgumentParser(
        description="PathManager CLI with usage examples"
    )
    #parser.add_argument(
    #    '--show', required=True,
    #    help='Show name (subdirectory under project root)'
    #)
    parser.add_argument(
        '--os', dest='default_os', choices=['win', 'linux', 'mac'],
        default='linux',
        help='Target OS for generated paths (win, linux, mac)'
    )
    args = parser.parse_args()

    # Create PathManager for the given show and OS
    pm = PathManagerFactory.create_for_show(
        studio_cfg=Path('C:/francesco/dev/src/o-pathmanager/o-pathmanager/configs/global.yaml'),
        projects_root=Path('C:/francesco/dev/src/o-pathmanager/o-pathmanager/configs/'),
        show_name='VEL',
        default_os=args.default_os
    )

    # 1) Print merged templates
    print("Merged Templates:\n")
    for name, conf in pm.get_templates().items():
        print(f"- {name}: {conf}")
    print("\n")

    rep_str = pm.generate(
        "sg_version_rep",
        { "color":      "RED",
        "resolution": "4K",
        "ext":        "EXR" }
    )

    print("SG Version Rep (Linux):", rep_str)

    version_name = pm.generate(
        "sg_version_name",
        { "show":            "VEL",
        "shotCode":        "shot05",
        "task":            "COMP",
        "sg_version_rep":  rep_str,
        "descriptor":      "FINAL",
        "version":         1 }
)
    published_file = pm.generate(
        "published_files",
        { "root":            "root",
         "seq":                "00",
        "shotCode":        "shot05",
        "task":              "COMP",
        "sg_version_name":  version_name,
        "eye":                 "l",
        "ext":               "exr" }
    )
    print("SG Version Name:", version_name)
    print("published file:", published_file)


if __name__ == '__main__':
    main()