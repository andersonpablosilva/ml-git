"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.hashfs import MultihashFS
from mlgit.cache import Cache
from mlgit.local import LocalRepository
from mlgit.utils import yaml_load, yaml_save, ensure_path_exists

import boto3
import botocore
from moto import mock_s3

import unittest
import tempfile
import os
import shutil
import hashlib

hs = {
	"zdj7WWsMkELZSGQGgpm5VieCWV8NxY5n5XEP73H4E7eeDMA3A",
	"zdj7We7Je5MRECsZUF7uptseHHPY29zGoqFsVHw6sbgv1MbWS",
	"zdj7WcMf5jG3dUpFVEqN38Rv2XAd6dNFuC91AvrQq4psha7qE",
	"zdj7WWG34cqLmcRe4CUEwevXr6TGdXPpM51yW85roL2LMs3PU",
	"zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
}

bucket = {
	"aws-credentials": {"profile": "personal"},
	"region": "us-east-1"
}
bucketname = "ml-git-datasets"

def md5sum(file):
	hash_md5 = hashlib.md5()
	with open(file, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

@mock_s3
class LocalRepositoryTestCases(unittest.TestCase):
	def setUp(self):
		client = boto3.client(
			"s3",
			region_name="us-east-1",
			aws_access_key_id="fake_access_key",
			aws_secret_access_key="fake_secret_key",
		)
		try:
			s3 = boto3.resource(
				"s3",
				region_name="us-east-1",
				aws_access_key_id="fake_access_key",
				aws_secret_access_key="fake_secret_key",
			)
			s3.meta.client.head_bucket(Bucket=bucketname)
		except botocore.exceptions.ClientError:
			pass
		else:
			err = "{bucket} should not exist.".format(bucket=bucketname)
			raise EnvironmentError(err)
		client.create_bucket(Bucket=bucketname)
		for h in hs:
			client.upload_file(Filename=os.path.join("hdata", h), Bucket=bucketname, Key=h)

	def test_push(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfspath = os.path.join(tmpdir, "hashfs-test")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			# r.push()

	def test_fetch(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mdpath = os.path.join(tmpdir, "metadata-test")
			c = yaml_load("hdata/config.yaml")

			specpath = os.path.join(mdpath, "vision-computing/images/dataset-ex")
			ensure_path_exists(specpath)
			shutil.copy("hdata/dataset-ex.spec", specpath + "/dataset-ex.spec")
			manifestpath = os.path.join(specpath, "MANIFEST.yaml")
			yaml_save({"zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh": {"imghires.jpg"}}, manifestpath)

			objectpath = os.path.join(tmpdir, "objects-test")
			spec = "vision-computing__images__dataset-ex__5"

			r = LocalRepository(c, objectpath)
			r.fetch(mdpath, spec)

			fs = set()
			for root, dirs, files in os.walk(objectpath):
				for file in files:
					fs.add(file)

			self.assertEqual(len(hs), len(fs))
			self.assertTrue(len(hs.difference(fs)) == 0)

	def test_get_update_cache(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put("hdata/imghires.jpg")

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			self.assertTrue(os.path.exists(cache._keypath(key)))
			self.assertEqual(md5sum("hdata/imghires.jpg"), md5sum(cache._keypath(key)))

	def test_get_update_links_wspace(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put("hdata/imghires.jpg")

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {"data/imghires.jpg"}
			r._update_links_wspace(cache, files, key, wspath, mfiles)

			wspace_file = os.path.join(wspath, "data/imghires.jpg")
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum("hdata/imghires.jpg"), md5sum(wspace_file))
			st = os.stat(wspace_file)
			self.assertTrue(st.st_nlink == 2)
			self.assertEqual(mfiles, {"data/imghires.jpg": "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"})

	def test_get_update_links_wspace_with_duplicates(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put("hdata/imghires.jpg")

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {"data/imghires.jpg", "data/imghires2.jpg"}
			r._update_links_wspace(cache, files, key, wspath, mfiles)

			wspace_file = os.path.join(wspath, "data/imghires.jpg")
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum("hdata/imghires.jpg"), md5sum(wspace_file))

			wspace_file = os.path.join(wspath, "data/imghires2.jpg")
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum("hdata/imghires.jpg"), md5sum(wspace_file))


			st = os.stat(wspace_file)
			self.assertTrue(st.st_nlink == 3)
			self.assertEqual(mfiles, {"data/imghires.jpg": "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh",
			                          "data/imghires2.jpg": "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"})


	def test_get_update_links_wspace_with_duplicates(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")
			ensure_path_exists(wspath)
			to_be_removed = os.path.join(wspath, "to_be_removed")
			with open(to_be_removed, "w") as f:
				f.write("DEAD\n")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put("hdata/imghires.jpg")

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {"data/imghires.jpg", "data/imghires2.jpg"}
			r._update_links_wspace(cache, files, key, wspath, mfiles)
			r._remove_unused_links_wspace(wspath, mfiles)

			self.assertFalse(os.path.exists(to_be_removed))


	# def test_xxx(self):
	# 	with tempfile.TemporaryDirectory() as tmpdir:
	# 		print(tmpdir)
	# 		hfs = MultihashFS(tmpdir)
	# 		hfs.put("hdata/imghires.jpg")
	#
	# 		for files in hfs.walk():
	# 			print(files)

	def tearDown(self):
		s3 = boto3.resource(
			"s3",
			region_name="eu-west-1",
			aws_access_key_id="fake_access_key",
			aws_secret_access_key="fake_secret_key",
		)
		bucket = s3.Bucket(bucketname)
		for key in bucket.objects.all():
			key.delete()
		bucket.delete()

if __name__ == "__main__":
	unittest.main()