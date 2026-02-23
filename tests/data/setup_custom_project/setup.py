import setuptools

setuptools.setup(
    name='test-custom-project',
    version='0.9.0',
    install_requires=['pyflakes'],
    setup_requires=['setuptools-odoo>=3.3.2'],
    odoo_addons=True,
    # force zip_safe which would otherwise be set to False via odoo_addons=True
    zip_safe=True,
)
