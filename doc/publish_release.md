# Release Guide

This is just an introduction how to publish releases manually.

This will be depreceated by using a CI tool.

## Requirements

Requirements before publishing project to public registry:
* Version is stable (ci pipeline success)
* All tests passed
* setup.cfg and setup.py validated

## Update Version

First upgrade project to new version using

```sh
bumpversion [ major | minor | patch ]
```

## Publish Version Of Library (travis)

Travis CI will automatically publish the project to PyPy registry if:
* project version was updated using `bumpversion`
* new version commited
* git `TAG` has beed created for commit

## Publish Version Of Library (manual)

### Init Workspace

if not done yet, add the account to be used for publishing the project

First make sure that your python package is up-to-date by installing it in your virtual env:
```sh
$ python -m pipenv install --dev
```
```sh
$ python -m pipenv shell
```
```sh
$ python setup.py install
```

### Step 1: Test Build Result

Before publishing the project to pypi registry, 
make sure the right sources will be added.

Pack the client library:
```sh
$ python setup.py sdist bdist_wheel
```

### Step 2: Publish

Publish the release with public access on test.pypi

```sh
$ twine upload -u username -p password --repository-url https://test.pypi.org/legacy/ dist/*
```

### Step 3: Check Result

Login to pypi and review the uploaded version:

https://test.pypi.org/project/msb-client-websocket-python/

### Step 2: Unpublish

Releases can be removed via WebUI. The removed version code cannot be reused!

## Test Project

Add the library to a test project and check its functionality:

```sh
$ pipenv install msb-client-websocket-python
```
