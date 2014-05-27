Testing application
===================

All tests for a module must be put into a subclass of ``TestCase`` (see docs for Flask-Testing extension).
Subclass needs to be in a separate module with a name that ends with ``_test.py``. For example,
tests for ``review.py`` would go into ``review_test.py``. If name of test module is different,
test runner is not going to find your test suite.

Server
------

To run all tests enter server's virtual enviroment and activate ``run_tests.py`` script::

    $ source ./env
    $ python run_tests.py