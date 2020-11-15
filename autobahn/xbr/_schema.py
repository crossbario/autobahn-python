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
from zlmdb.flatbuffers.reflection.BaseType import BaseType as _BaseType


class FbsType(object):
    None_ = _BaseType.None_
    UType = _BaseType.UType
    Bool = _BaseType.Bool
    Byte = _BaseType.Byte
    UByte = _BaseType.UByte
    Short = _BaseType.Short
    UShort = _BaseType.UShort
    Int = _BaseType.Int
    UInt = _BaseType.UInt
    Long = _BaseType.Long
    ULong = _BaseType.ULong
    Float = _BaseType.Float
    Double = _BaseType.Double
    String = _BaseType.String
    Vector = _BaseType.Vector
    Obj = _BaseType.Obj
    Union = _BaseType.Union

    FBS2PY = {
        _BaseType.None_: type(None),
        _BaseType.UType: int,
        _BaseType.Bool: bool,
        _BaseType.Byte: bytes,
        _BaseType.UByte: int,
        _BaseType.Short: int,
        _BaseType.UShort: int,
        _BaseType.Int: int,
        _BaseType.UInt: int,
        _BaseType.Long: int,
        _BaseType.ULong: int,
        _BaseType.Float: float,
        _BaseType.Double: float,
        _BaseType.String: str,
        _BaseType.Vector: List,
        _BaseType.Obj: object,
        _BaseType.Union: Union,
    }

    FBS2STR = {
        _BaseType.None_: 'None',
        _BaseType.UType: 'UType',
        _BaseType.Bool: 'Bool',
        _BaseType.Byte: 'Byte',
        _BaseType.UByte: 'UByte',
        _BaseType.Short: 'Short',
        _BaseType.UShort: 'UShort',
        _BaseType.Int: 'Int',
        _BaseType.UInt: 'UInt',
        _BaseType.Long: 'Long',
        _BaseType.ULong: 'ULong',
        _BaseType.Float: 'Float',
        _BaseType.Double: 'Double',
        _BaseType.String: 'String',
        _BaseType.Vector: 'Vector',
        _BaseType.Obj: 'Obj',
        _BaseType.Union: 'Union',
    }

    STR2FBS = {
        'None': _BaseType.None_,
        'UType': _BaseType.UType,
        'Bool': _BaseType.Bool,
        'Byte': _BaseType.Byte,
        'UByte': _BaseType.UByte,
        'Short': _BaseType.Short,
        'UShort': _BaseType.UShort,
        'Int': _BaseType.Int,
        'UInt': _BaseType.UInt,
        'Long': _BaseType.Long,
        'ULong': _BaseType.ULong,
        'Float': _BaseType.Float,
        'Double': _BaseType.Double,
        'String': _BaseType.String,
        'Vector': _BaseType.Vector,
        'Obj': _BaseType.Obj,
        'Union': _BaseType.Union,
    }


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


class FbsService(object):
    def __init__(self):
        pass


class FbsRPCCall(object):
    def __init__(self):
        pass


class FbsEnumValue(object):
    def __init__(self, name, value, docs):
        self._name = name
        self._value = value
        self._docs = docs


class FbsEnum(object):
    def __init__(self, name, values, is_union, underlying_type, attrs, docs):
        self._name = name
        self._values = values
        self._is_union = is_union
        self._underlying_type = underlying_type
        self._attrs = attrs
        self._docs = docs


class FbsSchema(object):
    """
    """
    def __init__(self,
                 filename: str,
                 root: _Schema,
                 objs: Dict[str, FbsObject],
                 enums: Dict[str, FbsEnum]):
        self._fn = os.path.abspath(filename)
        self._root = root
        self._objs = objs
        self._enums = enums

    def __str__(self):
        return 'Schema(filename="{}", root={}, objs={}, enums={})'.format(self._fn, self._root, self._objs, self._enums)

    @staticmethod
    def load(filename):
        if not os.path.isfile(filename):
            raise RuntimeError('cannot open schema file {}'.format(filename))
        with open(filename, 'rb') as fd:
            data = fd.read()

        print('processing schema {} ({} bytes) ..'.format(filename, len(data)))
        root = _Schema.GetRootAsSchema(data, 0)

        objs = {}
        enums = {}

        for i in range(root.EnumsLength()):
            fbs_enum = root.Enums(i)

            enum_name = fbs_enum.Name()
            if enum_name:
                enum_name = enum_name.decode('utf8')

            enum_values = {}
            for j in range(fbs_enum.ValuesLength()):
                fbs_enum_value = fbs_enum.Values(j)

                enum_value_name = fbs_enum_value.Name()
                if enum_value_name:
                    enum_value_name = enum_value_name.decode('utf8')

                enum_value_value = fbs_enum_value.Value()

                enum_value_docs = []
                for j in range(fbs_enum_value.DocumentationLength()):
                    enum_value_doc_line = fbs_enum_value.Documentation(j)
                    if enum_value_doc_line:
                        enum_value_doc_line = enum_value_doc_line.decode('utf8')
                        enum_value_docs.append(enum_value_doc_line)
                enum_value_docs = '\n'.join(enum_value_docs)

                enum_value = FbsEnumValue(name=enum_value_name, value=enum_value_value, docs=enum_value_docs)
                assert enum_value_name not in enum_values
                enum_values[enum_value_name] = enum_value

            enum = FbsEnum(name=enum_name, values=enum_values)
            assert enum_name not in enums
            enums[enum_name] = enum

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

        schema = FbsSchema(filename, root, objs, enums)
        return schema
