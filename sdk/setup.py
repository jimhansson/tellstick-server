# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	name='sdk',
	version='0.1',
	packages=['sdk'],
	entry_points = {
		'console_scripts': [
			'telldus = sdk.cli:main'
		],
		'distutils.commands': [
			'telldus_plugin = sdk.plugin:telldus_plugin'
		],
		'distutils.setup_keywords': [
			'color = sdk.plugin:telldus_plugin.validate_attribute',
			'compatible_platforms = sdk.plugin:telldus_plugin.validate_attribute',
			'icon = sdk.plugin:telldus_plugin.validate_attribute',
			'required_features = sdk.plugin:telldus_plugin.validate_attribute',
		],
	},
)
