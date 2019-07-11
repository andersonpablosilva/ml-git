"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.cache import Cache
from mlgit.utils import yaml_save
import unittest
import tempfile
import os


class CacheTestCases(unittest.TestCase):
	def test_update(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			print(tmpdir)
			manifest = os.path.join(tmpdir, 'manifest.yaml')
			yaml_save({"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u" : {"think-hires.jpg"}}, manifest)
			c = Cache(tmpdir, "data", manifest)
			c.update()
			st = os.stat("data/think-hires.jpg")
			self.assertEqual(st.st_nlink, 2)
			self.assertTrue(c.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))


if __name__ == "__main__":
	unittest.main()