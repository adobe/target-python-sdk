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

# Install dependencies - older versions of python need to bootstrap pip for CI workflow
install: env
ifneq (,$(filter $(PYTHON_VERSION),2.7))
		curl https://bootstrap.pypa.io/pip/${PYTHON_VERSION}/get-pip.py | python
endif
	python -m pip install --upgrade pip "setuptools>=38.3.0,<=44.1.x" wheel build pylint twine bump2version coverage
	python -m pip install -r requirements.txt
	python -m pip install -r test-requirements.txt

# Run tests and generate coverage
test: env build
	coverage run --omit="target_python_sdk/tests/*,target_tools/tests/*,target_decisioning_engine/tests/*" --source target_python_sdk,target_tools,target_decisioning_engine --module unittest discover

# View test coverage summary - coverage must first be generated by make test
coverage: env
	coverage report -m

# Format code - turn off linting for older versions of python due to collisions between current and old standards
format: env
ifneq (,$(filter $(PYTHON_VERSION),2.7))
		echo "Linting turned off for python version ${PYTHON_VERSION}"
else
		pylint target_python_sdk target_tools target_decisioning_engine
endif

# Generate client based on open-api spec
codegen:
	cd codegeneration && npm install && npm run precodegen && npm run codegen

# All the things to run on commit/PR open
pre_build: new_env clean install format test

# Create build package
build: env clean
	python -m build

# Publish package to Pypi
publish: env
	twine check dist/*
	twine upload dist/*

# Bump version for next release - i.e. make version_bump part=[patch, minor, major]
version_bump: env
	bump2version ${part}
