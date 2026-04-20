from pathlib import Path

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pbuilder.downloader import download_wheels, get_pkgs, generate_cache  # Replace with your actual filename

@pytest.fixture
def tmp_dir():
    return Path(__file__).parent / "tmp"


## --- Tests for function get_pkgs---
def test_get_pkgs_valid_file(tmp_path):
    """
    Test that valid packages are correctly parsed, while
    ignoring comments and empty lines.
    """
    # Create a temporary requirements file
    req_file = tmp_path / "requirements.txt"
    content = (
        "pandas==2.0.0\n"
        "  requests  \n"  # Leading/trailing spaces
        "# This is a comment\n"
        "\n"  # Empty line
        "numpy>=1.21.0\n"
    )
    req_file.write_text(content)

    # Execute
    result = get_pkgs(req_file)

    # Assertions
    expected = ["pandas==2.0.0", "requests", "numpy>=1.21.0"]
    assert result == expected
    assert len(result) == 3


def test_get_pkgs_file_not_found(capsys):
    """
    Test that a non-existent file returns an empty list and
    prints a clear error message.
    """
    non_existent = Path("ghost_file.txt")

    result = get_pkgs(non_existent)

    # Check return value
    assert result == []

    # Check if the error message was printed to stdout
    captured = capsys.readouterr()
    assert "Error: The provided requirements file" in captured.out
    assert "ghost_file.txt" in captured.out


def test_get_pkgs_empty_file(tmp_path):
    """
    Test that an empty file returns an empty list without error.
    """
    req_file = tmp_path / "empty.txt"
    req_file.write_text("")

    result = get_pkgs(req_file)
    assert result == []


def test_get_pkgs_only_comments(tmp_path):
    """
    Test that a file with only comments and whitespace returns an empty list.
    """
    req_file = tmp_path / "comments.txt"
    req_file.write_text("# Only comments\n   \n# More comments")

    result = get_pkgs(req_file)
    assert result == []


## --- Tests for function generate_cache ---

# Constants for testing (matches your script)
@pytest.fixture
def cache_file(tmp_dir):
    CACHE_FILE_NAME = ".cache_pkg"
    return tmp_dir / CACHE_FILE_NAME



def test_generate_cache_new_file(cache_file):
    """Test creating the cache file for the first time."""
    packages = [" pandas==2.0.0 ", "requests", " # ignore me "]

    success = generate_cache(packages, cache_file)
    assert success is True
    assert cache_file.exists()

    # Check content (should be stripped, deduplicated, and sorted)
    content = cache_file.read_text().splitlines()
    assert content == ["pandas==2.0.0", "requests"]


def test_generate_cache_merge_and_deduplicate(cache_file):
    """Test that existing cache content is merged and deduplicated."""
    # Pre-seed the cache
    cache_file.write_text("numpy\npandas==2.0.0\n")

    # Add one existing and one new package
    new_packages = ["pandas==2.0.0", "scipy"]

    success = generate_cache(new_packages, cache_file)

    assert success is True
    content = cache_file.read_text().splitlines()
    # Should be sorted: numpy, pandas, scipy
    assert content == ["numpy", "pandas==2.0.0", "scipy"]
    assert len(content) == 3


def test_generate_cache_io_error(cache_file, capsys):
    """Test handling of write permissions or other IOErrors."""
    # We mock the 'open' call specifically for writing to trigger an OSError
    with patch("pathlib.Path.open", side_effect=IOError("Disk Full")):
        success = generate_cache(["any-pkg"], cache_file)

        assert success is False
        captured = capsys.readouterr()
        assert "Error writing to" in captured.out
        assert "Disk Full" in captured.out


def test_generate_cache_empty_input(cache_file):
    """Test that providing an empty list doesn't crash the function."""
    # Ensure directory exists
    success = generate_cache([], cache_file)

    assert success is True
    # Should create an empty file if it didn't exist
    assert cache_file.exists()


## --- Tests for function download_wheels ---
def test_download_wheels_success(tmp_dir):
    """
    Test that the function correctly parses the file and calls pip wheel.
    """
    # 1. Setup: Create a dummy requirements.txt
    req_file = tmp_dir / "requirements.txt"
    req_file.write_text("pandas==2.0.0\n# comment\nrequests\n")

    out_dir = tmp_dir / "dist"

    # 2. Mock subprocess.run so we don't actually download anything
    with patch("subprocess.run") as mock_run:
        # Configure the mock to simulate a successful command
        mock_run.return_value = MagicMock(returncode=0)

        download_wheels(str(req_file), str(out_dir))

        # 3. Assertions
        # Check if the output directory was created
        assert out_dir.exists()

        # Check if subprocess.run was called for each non-comment line (2 packages)
        assert mock_run.call_count == 2

        # Verify the first call's arguments
        first_call_args = mock_run.call_args_list[0][0][0]
        assert "pip" in first_call_args
        assert "wheel" in first_call_args
        assert "pandas==2.0.0" in first_call_args


def test_download_wheels_file_not_found(capsys):
    """
    Test the behavior when the requirements file does not exist.
    """
    download_wheels("non_existent.txt", "./out")

    # Capture the print output
    captured = capsys.readouterr()
    assert "Error: non_existent.txt not found." in captured.out


def test_download_wheels_subprocess_failure(tmp_dir, capsys):
    """
    Test that the script handles a pip failure gracefully.
    """
    req_file = tmp_dir / "reqs.txt"
    req_file.write_text("bad-package-name")
    out_dir = tmp_dir / "dist"

    with patch("subprocess.run") as mock_run:
        # Simulate a subprocess error
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="pip wheel...",
            stderr="Could not find version"
        )

        download_wheels(str(req_file), str(out_dir))

        captured = capsys.readouterr()
        assert "[ERROR] Failed to process bad-package-name" in captured.out


def test_download_wheels_with_file_success(tmp_dir):
    # 1. Setup: Create a dummy requirements.txt
    req_file = tmp_dir / "requirements_ap_hp.txt"

    out_dir = tmp_dir / "out" / "ap_hp"

    download_wheels(str(req_file), str(out_dir))
