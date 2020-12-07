from main import main, REPORT_PATH
from utils import path_join_current
import os


def test_main():
    main(REPORT_PATH)
    assert os.path.exists(path_join_current(REPORT_PATH))
