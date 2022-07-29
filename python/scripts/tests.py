import os
import unittest
from pathlib import Path

directory = os.path.join(Path.cwd(), "test")

loader = unittest.TestLoader()
suite = loader.discover(start_dir=directory, pattern="*_test.py")
runner = unittest.TextTestRunner()

runner.run(suite)
