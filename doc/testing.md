# Testing Guide

This is an overview on how to test the project.

## Prerequisites

- python and pip installed: https://www.python.org/downloads/

## Install requirements

Install the required python modules in a virtual environment

```sh
$ python -m pipenv install --dev
```

```sh
$ python -m pipenv shell
```

```sh
$ python setup.py install
```

## Code Style Test

We use `flake8` and base on `pep8`.

After you have changed code, check for new pep8 or other issues
```sh
$ flake8
```

Possible rule violations are listed here: https://eslint.org/docs/rules/

Some rules can be auto-fixed by eslint
```sh
$ autopep8 ./ --recursive --in-place --verbose
```

## Unit Test

Run `unit tests`

```sh
$ pytest -s test/test_unit.py
```

## Integration Test

Run `integration tests` against local or remote MSB instance.

Set IP of MSB server and use standard ports:
```sh
$ TESTENV_CUSTOMIP=10.15.26.7 pytest -s test/test_integration.py
```

Or define urls for webscoket inteface, smart object management and flow management:
```sh

```

## All Test

Run `all tests`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 pytest -s
```

## Test Coverage

The coverage framework `pytest-cov` is used.

Check `unit test coverage`

```sh
$ pytest -s --cov=msb_client  test/test_unit.py
```

Check `integration test coverage`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 pytest -s --cov=msb_client test/test_integration.py
```

Check `all test coverage`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 pytest -s --cov=msb_client
```

Generate `html report`
```sh
$ TESTENV_CUSTOMIP=10.15.26.7 pytest -s --cov=msb_client --cov-report html:./Output/coverage
```

