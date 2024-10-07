from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in e_desk/__init__.py
from e_desk import __version__ as version

setup(
	name="e_desk",
	version=version,
	description="E Desk",
	author="sathya",
	author_email="sathya@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
