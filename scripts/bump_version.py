#!/usr/bin/env python3
"""
Version bumping script for code2llm
Updates version in pyproject.toml and VERSION file
"""

import sys
import re
from pathlib import Path

def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)
    
    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        print("Error: version not found in pyproject.toml")
        sys.exit(1)
    
    return match.group(1)

def parse_version(version_str):
    """Parse version string into tuple of (major, minor, patch)"""
    parts = version_str.split('.')
    return tuple(int(x) for x in parts[:3])

def format_version(major, minor, patch):
    """Format version tuple as string"""
    return f"{major}.{minor}.{patch}"

def bump_version(version_type):
    """Bump version based on type (major, minor, patch)"""
    current = get_current_version()
    major, minor, patch = parse_version(current)
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid version type '{version_type}'. Use major, minor, or patch.")
        sys.exit(1)
    
    new_version = format_version(major, minor, patch)
    return new_version

def update_pyproject_toml(new_version):
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    # Update version line
    content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(content)
    print(f"Updated pyproject.toml to version {new_version}")

def update_version_file(new_version):
    """Update VERSION file"""
    version_path = Path("VERSION")
    version_path.write_text(f"{new_version}\n")
    print(f"Updated VERSION file to {new_version}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)
    
    version_type = sys.argv[1].lower()
    if version_type not in ["major", "minor", "patch"]:
        print("Error: version_type must be major, minor, or patch")
        sys.exit(1)
    
    current_version = get_current_version()
    new_version = bump_version(version_type)
    
    print(f"Bumping {version_type} version: {current_version} -> {new_version}")
    
    update_pyproject_toml(new_version)
    update_version_file(new_version)

if __name__ == "__main__":
    main()
