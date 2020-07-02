import os
import glob
import warnings
import subprocess
from setuptools import setup, find_packages

install_requires = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "requirements.txt"))]

with open("README.md") as fh:
    long_description = fh.read()

def get_version():
    filepath = os.path.join(os.path.dirname(__file__), "cli_builder", "version.py")
    if os.path.isfile(filepath):
        # In source distributions or builds, version is available in the generated cli_builder/version.py file
        with open(filepath) as fh:
            version = dict()
            exec(fh.read().strip(), version)
            return version['__version__']
    else:
        p = subprocess.run(["git", "describe", "--tags", "--match", "v*.*.*"], stdout=subprocess.PIPE)
        if 128 == p.returncode:
            warnings.warn('There are no git tags with version information. '
                          'To tag the first commit as v0.0.0 use '
                          '`git tag --annotate "v0.0.0" $(git rev-list --max-parents=0 HEAD) -m "v0.0.0"`')
            return "0"
        else:
            p.check_returncode()
            out = p.stdout.decode("ascii").strip()
            if "-" in out:
                out = out.split("-", 1)[0]
            assert out.startswith("v")
            return out[1:]

setup(
    name="cli-builder",
    version=get_version(),
    description="Decorators for building command group CLIs",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/xbrianh/cli-builder",
    author="Brian Hannafious",
    author_email="bhannafi@ucsc.edu",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    scripts=glob.glob("scripts/*"),
    zip_safe=False,
    install_requires=install_requires,
    platforms=["MacOS X", "Posix"],
    test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7"
    ]
)
