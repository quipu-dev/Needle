import os
import sys
import glob
import shutil
import subprocess
import requests
import tomli
from pathlib import Path
from packaging.version import parse as parse_version

# Configuration
WORKSPACE_ROOT = Path(__file__).parent.parent
DIST_DIR = WORKSPACE_ROOT / "dist"
PYPI_JSON_URL = "https://pypi.org/pypi/{package_name}/json"

def run_command(cmd, cwd=None, env=None, check=True):
    """Run a shell command."""
    print(f"Executing: {cmd}")
    try:
        subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            env=env, 
            check=check, 
            stdout=sys.stdout, 
            stderr=sys.stderr
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if check:
            sys.exit(1)

def get_workspace_packages():
    """Discover packages from the root pyproject.toml."""
    pyproject_path = WORKSPACE_ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        config = tomli.load(f)
    
    # Try to find workspace members definition (uv style)
    members = config.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    
    if not members:
        print("⚠️ No workspace members found in [tool.uv.workspace].")
        return []

    package_paths = []
    for member_glob in members:
        # Expand glob (e.g., "packages/*") relative to root
        full_glob = str(WORKSPACE_ROOT / member_glob)
        found = glob.glob(full_glob)
        package_paths.extend([Path(p) for p in found if (Path(p) / "pyproject.toml").exists()])
    
    # Sort for consistent logging
    return sorted(package_paths)

def get_local_info(package_path):
    """Extract name and version from a package's pyproject.toml."""
    with open(package_path / "pyproject.toml", "rb") as f:
        data = tomli.load(f)
    
    project = data.get("project", {})
    return project.get("name"), project.get("version")

def get_remote_version(package_name):
    """Fetch the latest version from PyPI."""
    url = PYPI_JSON_URL.format(package_name=package_name)
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            return None # Package not published yet
        resp.raise_for_status()
        data = resp.json()
        return data["info"]["version"]
    except Exception as e:
        print(f"⚠️ Could not fetch version for {package_name}: {e}")
        return None

def publish_package(package_path, pkg_name, version):
    """Build, Upload, and Tag."""
    print(f"\n🚀 Starting release process for {pkg_name} v{version}...")
    
    # 1. Clean previous builds
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    
    # 2. Build
    run_command(f"{sys.executable} -m build {package_path} --outdir {DIST_DIR}")
    
    # 3. Upload
    # Assumes TWINE_USERNAME and TWINE_PASSWORD (or token) are in env
    run_command(f"twine upload {DIST_DIR}/*")
    
    # 4. Git Tag
    tag_name = f"{pkg_name}/v{version}"
    print(f"🏷️ Tagging repository: {tag_name}")
    run_command(f"git tag {tag_name}")
    run_command(f"git push origin {tag_name}")

def main():
    print("🔍 Scanning workspace for release candidates...")
    packages = get_workspace_packages()
    print(f"Found {len(packages)} packages.")

    for pkg_path in packages:
        name, local_ver_str = get_local_info(pkg_path)
        if not name or not local_ver_str:
            print(f"⏩ Skipping {pkg_path.name}: Missing name or version.")
            continue
            
        remote_ver_str = get_remote_version(name)
        
        should_release = False
        if remote_ver_str is None:
            print(f"🆕 {name}: Not found on PyPI. First release!")
            should_release = True
        else:
            local_ver = parse_version(local_ver_str)
            remote_ver = parse_version(remote_ver_str)
            
            if local_ver > remote_ver:
                print(f"✨ {name}: Update detected ({remote_ver} -> {local_ver})")
                should_release = True
            else:
                print(f"💤 {name}: Up to date ({local_ver})")
        
        if should_release:
            publish_package(pkg_path, name, local_ver_str)
            print(f"✅ {name} released successfully.\n")

if __name__ == "__main__":
    main()