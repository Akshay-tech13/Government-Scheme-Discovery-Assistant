# conftest.py — makes the scheme_assistant package importable from the tests directory.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
