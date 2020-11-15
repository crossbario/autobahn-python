###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2018 Luis Teixeira
# - copied & modified from https://github.com/vergl4s/ethereum-mnemonic-utils
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import os
from typing import List, Dict
from zlmdb.flatbuffers.reflection.Schema import Schema as _Schema


class FbsObject(object):
    def __init__(self, name: str, docs: str):
        self._name = name
        self._docs = docs

    @property
    def name(self):
        return self._name

    @property
    def docs(self):
        return self._docs



class FbsSchema(object):
    """
    """
    def __init__(self, filename: str, root: _Schema, objs: Dict[str, FbsObject]):
        self._fn = os.path.abspath(filename)
        self._root = root
        self._objs = objs

    def __str__(self):
        s = 'Schema(filename="{}", root={}, objs={})'.format(self._fn, self._root, self._objs)
        return s

    @staticmethod
    def load(filename):
        if not os.path.isfile(filename):
            raise RuntimeError('cannot open schema file {}'.format(filename))
        with open(filename, 'rb') as fd:
            data = fd.read()

        print('processing schema {} ({} bytes) ..'.format(filename, len(data)))
        root = _Schema.GetRootAsSchema(data, 0)

        objs = {}

        for i in range(root.ObjectsLength()):
            fbs_obj = root.Objects(i)
            name = fbs_obj.Name()
            if name:
                name = name.decode('utf8')
            docs = []
            for j in range(fbs_obj.DocumentationLength()):
                doc_line = fbs_obj.Documentation(j)
                if doc_line:
                    doc_line = doc_line.decode('utf8')
                    docs.append(doc_line)
            docs = '\n'.join(docs)
            obj = FbsObject(name=name, docs=docs)
            assert name not in objs
            objs[name] = obj

        schema = FbsSchema(filename, root, objs)
        return schema
