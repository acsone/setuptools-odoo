Developer instructions
~~~~~~~~~~~~~~~~~~~~~~

How to run tests
----------------

* run ``tox`` (if not installed ``apt-get install tox``)

How to build the documentation
------------------------------

Documentation is built automatically at http://setuptools-odoo.readthedocs.io/.

To build it locally:

* pip install -e .
* pip install sphinx
* cd docs
* make html

How to release
--------------

* update changelog in CHANGES.rst, referring to the next version
* python setup.py check --restructuredtext
* commit everything
* make sure tests pass!
* git tag <version>, where <version> is PEP 440 compliant
* git push --tags

Uploading of tagged versions to pypi will be taken care of by travis.
