.PHONY: clean install codegen format test build

all: pre_env clean install codegen format test build

pre_env:
	${PYTHON_PATH} -m pip install --upgrade virtualenv
env: 
	test -d env/bin || ${PYTHON_PATH} -m virtualenv env
	. env/bin/activate
clean_env:
	rm -rf env

# Setup new virtual env (deletes existing one)
new_env: clean_env pre_env env

clean:
	rm -rf build dist target_python_sdk.egg-info

# Install dependencies - pip update sometimes required for python 2.7
install: env
	curl https://bootstrap.pypa.io/get-pip.py | python
	pip install --upgrade pip "setuptools>=38.3.0,<=44.1.x" wheel pep517 pylint twine bump2version pytest coverage coveralls

# Run tests
test: env
	coverage run --source src --module pytest tests

# Format code
format: env
	pylint src tests

# Generate client based on open-api spec
codegen:
	cd codegeneration && npm install && npm run codegen

# All the things to run on commit/PR open
pre_build: new_env clean install format test

# Create build package
build: env
	python -m pep517.build .

# Publish package to Pypi
publish:
	twine check dist/*
	twine upload dist/*

# Bump version for next release - i.e. make version_bump part=[patch, minor, major]
version_bump:
	bump2version ${part}
