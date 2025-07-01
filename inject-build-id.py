#!python

import os

if __name__ == "__main__":
    _EVAR = "AUTOBAHN_BUILD_ID"
    _SEARCH = "__build__ = u'00000'"
    _REPLACE = "__build__ = u'{}'"

    if _EVAR in os.environ:
        files = []
        try:
            from autobahn import _version
        except ImportError:
            pass
        else:
            files.append(os.path.abspath(_version.__file__))

        fn = "autobahn/_version.py"
        if os.path.exists(fn):
            files.append(os.path.abspath(fn))

        done = []

        for fn in files:
            if fn in done:
                print('Skipping file "{}": already processed'.format(fn))
            else:
                with open(fn) as f:
                    contents = f.read()
                build_id_stmt = _REPLACE.format(os.environ[_EVAR])
                if contents.find(_SEARCH):
                    contents = contents.replace(_SEARCH, build_id_stmt)
                    print(contents)
                    with open(fn, "w") as f:
                        f.write(contents)
                        f.flush()
                    print(
                        'Ok: replaced placeholder build ID in file "{}" with "{}"'.format(
                            fn, build_id_stmt
                        )
                    )
                    done.append(fn)
                else:
                    if contents.find(build_id_stmt):
                        print('Skipping file "{}": build ID already correct')
                    else:
                        error_msg = 'Error: could not find search string "{}" to inject build ID in file "{}"'.format(
                            _SEARCH, _version.__file__
                        )
                        raise Exception(error_msg)
    else:
        print("Skipping injection of build ID: AUTOBAHN_BUILD_ID not set")
