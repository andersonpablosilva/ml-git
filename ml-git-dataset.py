"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python3

from mlgit.config import config_load, list_repos
from mlgit.log import init_logger
from mlgit.dataset_manager import DatasetManager
from mlgit.options import parsed_options

if __name__=="__main__":
	config = config_load()
	init_logger()

	args = parsed_options("dataset")

	if args.cmd == "add":
		dataset_spec = args.dataset
		#repo = args.repository
		m = DatasetManager(config)
		m.dataset_store(dataset_spec)
	if args.cmd == "get":
		dataset_spec = args.dataset
		repo = args.repository
		m = DatasetManager(config)
		m.dataset_get(dataset_spec)
	#elif arg1 == "search":
	if args.cmd == "list":
		repo = args.repository
		m = DatasetManager(config)
		m.list()
	if args.cmd == "show":
		dataset_name = args.dataset
		repo = args.repository
		repos = [repo]
		if repo == "all":
			repos = list_repos()
		print(repos)
		for repo in repos:
			print("*** %s ***" % (config))
			m = DatasetManager(config)
			m.show(dataset_name)
			print
	if args.cmd == "publish":
		repo = args.repository
		m = DatasetManager(config)
		m.publish()
	if args.cmd == "update":
		repo = args.repository
		m = DatasetManager(config)
		m.update()