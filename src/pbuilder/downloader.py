import subprocess
import sys
from pathlib import Path
from typing import List, Union

CACHE_FILE_NAME = ".cache_pkg"


def get_pkgs(req_path: Path) -> List[str]:
    """
    This function read a requirements file and return a list of all packages
    :param req_path: the requirements file path
    :return: A list of all packages
    """
    if not req_path.exists():
        print(f"Error: The provided requirements file at {req_path.as_posix()} is not found.")
        return []
    # we don't use the entire file, because we want better error handling
    with open(req_path, "r") as f:
        # Read lines and strip whitespace/comments
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return packages


def generate_cache(packages: List[str], cache_path: Path) -> bool:
    """
    This function generates a requirement.txt like cache file for all the downloaded packages
    :param packages: The list of all the downloaded packages
    :param cache_path: The destination path
    :return:
    """
    # step1: clean the newly downloaded packages

    # 1. Use a set comprehension for better performance and readability
    # 2. .strip() only removes the whitespace at the edges
    # 3. We ensure we don't include empty lines or just whitespace
    new_packages = {
        pkg.strip()
        for pkg in packages
        if pkg.strip() and not pkg.strip().startswith("#")
    }

    # step2: If the cache file exists deja, read existing packages and merge them with our new set
    if cache_path.exists():
        try:
            existing_pkgs = get_pkgs(cache_path)
            new_packages.update(existing_pkgs)
        except IOError as e:
            print(f"--- Warning: Could not read existing cache {cache_path}: {e} ---")

    # step3: Write the combined, sorted set back to the file
    try:
        # 2. Write using a context manager (best practice)
        # We use newline='\n' to ensure consistent line endings across OS
        with cache_path.open("w", encoding="utf-8", newline='\n') as f:
            for package in sorted(new_packages):
                f.write(f"{package}\n")

        print(f"--- Cache updated at {cache_path.name} (Total: {len(new_packages)} packages) ---")
        return True

    except IOError as e:
        print(f"--- Error writing to {cache_path}: {e} ---")
        return False


def write_success_pkgs(pkgs: List[str], dest_path: Path) -> bool:
    req_path = Path(requirements_file)


def download_wheels(requirements_file: str, output_dir: str):
    """
    Downloads sources and builds wheels locally so the air-gapped
    server doesn't need a compiler.
    """
    req_path = Path(requirements_file)
    dest_path = Path(output_dir)
    success_pkgs = []
    # store failed pkgs, if pip wheel can't compile or download the pkg.
    failed_pkgs = {}
    # step 1: parse the req file and get the package list,
    packages = get_pkgs(req_path)

    # step2: Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting download packages to: {dest_path.absolute()} ---")

    # step3: get cached packages list
    # to avoid redownload everything, we cached the download or complied .wheel file
    cache_path = dest_path / CACHE_FILE_NAME
    cache_pkgs = get_pkgs(cache_path)

    # step4: download or compile the .wheel file
    for package in packages:
        print(f"Processing: {package}...")
        if package in cache_pkgs:
            print(f"package {package} already downloaded: skipping...")
            continue
        # 'pip wheel' is the one-stop-shop for your requirements:
        # 1. It checks if a wheel exists (downloads it).
        # 2. If no wheel exists, it builds one from source.
        # 3. It handles dependencies automatically.
        cmd = [
            sys.executable, "-m", "pip", "wheel",
            "--wheel-dir", str(dest_path),
            "--find-links", str(dest_path),  # Check local dir first to avoid re-downloads
            package
        ]

        try:
            # We use subprocess.run to execute the command for each row
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  [OK] {package} is ready in {output_dir}")
            success_pkgs.append(package)
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to process {package}: {e.stderr}")
            failed_pkgs[package] = e.stderr
    # step 5: update cache
    generate_cache(success_pkgs, cache_path)
    print(f"\n--- All done! ---")
    print(f"Files stored in: {dest_path.absolute()}")
