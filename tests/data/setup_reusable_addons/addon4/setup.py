import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'addon1': 'odoo-addon-addon1>=8.0.3.0.0,<9.0a',
        },
        'external_dependencies_override': {
            'python': {
                'astropy': 'astropy>=1.0',
            },
        },
    },
)
