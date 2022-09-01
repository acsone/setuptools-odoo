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

* in the ``setuptools_odoo`` directory, run ``../mk_base_addons```
* update changelog in CHANGES.rst, by running ``towncrier --version <version>``
* python setup.py check --restructuredtext
* commit everything
* make sure tests pass!
* create a release with a tag on GitHub, the CI will build and publish to PyPI

Uploading of tagged versions to pypi will be taken care of by travis.
