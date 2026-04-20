import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pbuilder.downloader import download_wheels  # Replace with your actual filename


## --- Tests ---
def test_download_wheels_success(tmp_path):
    """
    Test that the function correctly parses the file and calls pip wheel.
    """
    # 1. Setup: Create a dummy requirements.txt
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("pandas==2.0.0\n# comment\nrequests\n")

    out_dir = tmp_path / "dist"

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


def test_download_wheels_subprocess_failure(tmp_path, capsys):
    """
    Test that the script handles a pip failure gracefully.
    """
    req_file = tmp_path / "reqs.txt"
    req_file.write_text("bad-package-name")
    out_dir = tmp_path / "dist"

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