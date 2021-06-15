# Adobe Target Python SDK

[![Coverage Status](https://coveralls.io/repos/github/adobe/target-python-sdk/badge.svg?branch=main)](https://coveralls.io/github/adobe/target-python-sdk?branch=main)

### Requirements
All currently maintained versions of Python are supported, see [Python Releases](https://www.python.org/downloads/).
Older Python releases may likely work too, but are not officially supported.
```
NPM 6+ (required by openapi-generator-cli)
Java 8+ (required by openapi-generator)
GNU Make
```

### Set PYTHON_PATH

Various build commands are supported via Makefile, but first you must export environment variable PYTHON_PATH to specify which python install to use to set up your virtual env.

```bash
$ export PYTHON_PATH=python2.7  # Symlink to Mac OS built-in version of python
$ export PYTHON_PATH=/usr/local/bin/python3
```

### Setup virtual env to make it easy to switch between python 2.7 and 3

```bash
$ make new_env          # Deletes existing virtual env and creates new one based on PYTHON_PATH
$ make install          # Install dependencies in virtual env
```

### Code generation

The SDK depends on [Target Open API](https://github.com/adobe/target-openapi). It uses Open API and the `Open API generator` to generate the low level HTTP client.

To be able to use `Target Open API` for code generation, we are leveraging Git subtree.

To import `Target Open API` as `openapi` folder please use commands:

```bash
$ git subtree add --prefix openapi git@github.com:adobe/target-openapi.git main --squash
```

To refresh the imported subtree use this command:

```bash
$ git subtree pull --prefix openapi git@github.com:adobe/target-openapi.git main --squash
```

Once all the tools are installed, there is no need to invoke them directly, everything is wrapped in a `Makefile` command, which can be invoked by running:

```bash
$ make codegen
```

### Run tests and format code

```bash
$ make test
$ make format
```

### Release build package

Releases are triggered through Github publish workflow. Input version part to update before publishing to pypi - [patch, minor, major]

#### Running Github Workflows on forked repositories

Github Workflows don't run on forked repositories by default.
You must enable GitHub Actions in the Actions tab of the forked repository.

See more details at https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows#pull-request-events-for-forked-repositories

## Contributing

Contributions are welcomed! Read the [Contributing Guide](CONTRIBUTING.md) for more information.

## Licensing

This project is licensed under the Apache V2 License. See [LICENSE](LICENSE) for more information.
