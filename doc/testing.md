# Testing Guide

This is an overview on how to test the project.

## Prerequisites

- python and pip installed: https://www.python.org/downloads/

## Install requirements

Install the required python modules in a virtual environment

Setup pipenv to develop in a virtual environment
```sh
$ pip install pipenv
```
```sh
$ python -m pipenv install --dev
```

And always run your development inside the pipenv shell
```sh
$ python -m pipenv shell
```

This will ensure that you use a virtual environment that is separated from the global python packages.

Install the msb_client python package in the virtual environment:
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
$ python -m pytest -s test/test_unit.py
```

## Integration Test

Run `integration tests` against local or remote MSB instance.

Set IP of MSB server and use standard ports:
```sh
$ TESTENV_CUSTOMIP=10.15.26.7 python -m pytest -s test/test_integration.py
```

Or define urls for webscoket inteface, smart object management and flow management:
```sh
$ TESTENV_BROKER_URL=https://ws.15xr.msb.oss.cell.vfk.fraunhofer.de/ \
TESTENV_SO_URL=https://so.15xr.msb.oss.cell.vfk.fraunhofer.de/ \
TESTENV_FLOW_URL=https://flow.15xr.msb.oss.cell.vfk.fraunhofer.de/ \
python -m pytest -s test/test_integration.py
```

Or define urls and run integration test with powershell

```cmd
> $env:TESTENV_BROKER_URL="https://ws.15xr.msb.oss.cell.vfk.fraunhofer.de/"
> $env:TESTENV_SO_URL="https://so.15xr.msb.oss.cell.vfk.fraunhofer.de/"
> $env:TESTENV_FLOW_URL="https://flow.15xr.msb.oss.cell.vfk.fraunhofer.de/"
> $env:TESTENV_OWNER_UUID="f10cfa25-58d4-41ba-8ecf-60ced3d60677"
> pytest -s test/test_integration.py
```

## All Test

Run `all tests`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 python -m pytest -s
```

## Test Coverage

The coverage framework `pytest-cov` is used.

Check `unit test coverage`

```sh
$ python -m pytest -s --cov=msb_client  test/test_unit.py
```

Check `integration test coverage`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 python -m pytest -s --cov=msb_client test/test_integration.py
```

Check `all test coverage`

```sh
$ TESTENV_CUSTOMIP=10.15.26.7 python -m pytest -s --cov=msb_client
```

Generate `html report`
```sh
$ TESTENV_CUSTOMIP=10.15.26.7 python -m pytest -s --cov=msb_client --cov-report html:./Output/coverage
```

## Issues

How to improve python shell formatting in git bash on windows:
```sh
alias python='winpty python.exe'
```
