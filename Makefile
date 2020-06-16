include common.mk

MODULES=cli_builder tests

test: lint mypy tests

lint:
	flake8 $(MODULES) *.py

mypy:
	mypy --ignore-missing-imports --no-strict-optional $(MODULES)

tests:
	PYTHONWARNINGS=ignore:ResourceWarning coverage run --source=cli_builder \
		-m unittest discover --start-directory tests --top-level-directory . --verbose

version: cli_builder/version.py

cli_builder/version.py: setup.py
	echo "__version__ = '$$(python setup.py --version)'" > $@

clean:
	git clean -dfx

build: clean version
	python setup.py bdist_wheel

install: build
	pip install --upgrade dist/*.whl

.PHONY: test lint mypy tests clean build install
