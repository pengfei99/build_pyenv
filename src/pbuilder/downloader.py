import subprocess
import sys
from pathlib import Path

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
    if not req_path.exists():
        print(f"Error: {requirements_file} not found.")
        return

    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)

    # step 1: get the package list, we don't use the entire file, because we want better error handling
    with open(req_path, "r") as f:
        # Read lines and strip whitespace/comments
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"--- Starting download packages to: {dest_path.absolute()} ---")

    for package in packages:
        print(f"Processing: {package}...")

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

    print(f"\n--- All done! ---")
    print(f"Files stored in: {dest_path.absolute()}")
