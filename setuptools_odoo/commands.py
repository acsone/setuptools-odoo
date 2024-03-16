# -*- coding: utf-8 -*-
try:
    from setuptools.command.editable_wheel import editable_wheel
except ImportError:
    compat_editable_wheel = None
else:

    class compat_editable_wheel(editable_wheel):
        def initialize_options(self):
            super().initialize_options()
            # Enforce the "compat" editable mode which simply adds the project
            # directory to sys.path with a .pth file, so Odoo will detect the addon
            # in the odoo/addons directory/namespace package.
            self.mode = "compat"
