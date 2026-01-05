#!/usr/bin/env python3
import re
import subprocess
import sys

ALLOWED_TOP_LEVEL = {
    "README.md",
    ".gitignore",
    ".pre-commit-config.yaml",
}

ALLOWED_PREFIXES = (
    ".github/",
    "scripts/",
    ".git/"
)

PAT = re.compile(
    r"^(?P<dept>mat|csc|sta)/"
    r"(?P<course>[abcd]\d{2})/"
    r"(?P<year>(?:19|20)\d{2})/"
    r"(?P<sem>fall|winter|summer)"
    r"(?P<rest>/.*)?$"
)


def tracked_files():
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def validate_paths(files):
    invalid_paths = []
    existing_readmes = []
    course_dirs = []

    for path in files:
        if path in ALLOWED_TOP_LEVEL or path.startswith(ALLOWED_PREFIXES):
            continue

        if not (m := PAT.fullmatch(path)):
            invalid_paths.append(path)
            continue

        sem = f"{m.group('dept')}/{m.group('course')}/{m.group('year')}/{m.group('sem')}"
        course_dirs.append(sem)

        if path == f'{sem}/README.md':
            existing_readmes.append(sem)

    return invalid_paths, existing_readmes, course_dirs


def missing_readmes(readmes, course_dirs):
    out = []
    for course_dir in course_dirs:
        if course_dir not in readmes:
            out.append(course_dir)
    return out


paths = tracked_files()
invalid_paths, existing_readmes, course_dirs = validate_paths(paths)
missing_readmes = missing_readmes(existing_readmes, course_dirs)

if not invalid_paths and not missing_readmes:
    print('No issues found')
    sys.exit(0)

if invalid_paths:
    print('These files violate repo structure')
    for path in invalid_paths:
        print(f'    {path}')

if missing_readmes:
    print('These course directories are missing README.md')
    for path in missing_readmes:
        print(f'    {path}')

sys.exit(1)
