# https://github.com/pyinstaller/pyinstaller/issues/3390

import sys

# this creates module: sys.modules['twisted.internet.reactor']
if sys.platform in ["win32"]:
    from twisted.internet.iocpreactor import reactor as _iocpreactor

    _iocpreactor.install()
else:
    from twisted.internet import default

    default.install()
