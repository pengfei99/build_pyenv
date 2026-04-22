from pathlib import Path

from pbuilder.downloader import download_wheels
from pbuilder.log_manager import setup_logger

def main():
    # setup logger
    log_path = Path(__file__).parent / "logs"
    setup_logger(log_dir=log_path)
    # setup parameters
    test_dir = "C:/Users/pliu/Documents/git/build_pyenv/tests/tmp/out/proj1"
    test_req = "C:/Users/pliu/Documents/git/build_pyenv/tests/tmp/proj1.txt"
    download_wheels(test_req, test_dir)


if __name__ == "__main__":
    main()
