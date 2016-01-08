## django_bench_runner - Locate slow tests

[![Build Status](https://secure.travis-ci.org/scuml/django-bench-runner.png?branch=master)](http://travis-ci.org/scuml/django-bench-runner)
[![Downloads](https://img.shields.io/pypi/dw/django-bench-runner.svg)](https://pypi.python.org/pypi/django-bench-runner)

Django Bench Runner is a drop-in enhancement of the default django test runner that times how long it takes to run individual tests.  It helps detect tests that might need optimization.

### Installation

    pip install django-bench-runner

In settings.py, add:

    TEST_RUNNER = 'django_bench_runner.runner.BenchRunner'

### Usage

Add the `-b` (or `--benchmark`) flag when running your tests.

### Colorization

Tests that run under .5 seconds are colored green.  The resulting tests are divvied into 3 groups.  The fastest third (yellow), the middle third (magenta), and the slowest third (red).  [Red tests do not mean the tests are necessarily bad or in critical need of a speedup](http://www.obeythetestinggoat.com/fast-tests-useless-hot-lava-be-damned.html).  It is just a graphical way to identify the various times of the tests.

### Example Output


    $ ./manage.py test core.tests.test_transfer_money -b --keepdb
    Using existing test database for alias 'default'...
    ..

    Test                                                              Runtime    Percent
    --------------------------------------------------------------  ---------  ---------

    core.tests.test_transfer_money.TestReleaseAmounts
    : test_wells_fargo                                                8.25052     47.81%
    : test_wells_fargo_exempt_from_prefunding                         9.00663     52.19%
    ---------------------------                                       -------    -------
    TestReleaseAmounts                                               17.25715    100.00%

    ----------------------------------------------------------------------
    Ran 2 tests in 17.262s

    OK

### Django compatibility

Tested and working in Django 1.8 and 1.9.


###### Credits
*Special thanks Sergey Astanin for [tabulate](https://pypi.python.org/pypi/tabulate)*
