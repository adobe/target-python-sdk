# Adobe Target Python SDK

### Requirements
```
Python 2.7+ or 3.4+
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

### Create build package
```bash
$ make build
```  
