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
import pprint
import hashlib
from typing import List, Dict

from zlmdb.flatbuffers.reflection.Schema import Schema as _Schema
from zlmdb.flatbuffers.reflection.BaseType import BaseType as _BaseType


def parse_attr(obj):
    attrs = {}
    for j in range(obj.AttributesLength()):
        fbs_attr = obj.Attributes(j)
        attr_key = fbs_attr.Key()
        if attr_key:
            attr_key = attr_key.decode('utf8')
        attr_value = fbs_attr.Value()
        if attr_value:
            attr_value = attr_value.decode('utf8')
        assert attr_key not in attrs
        attrs[attr_key] = attr_value
    return attrs


def parse_docs(obj):
    docs = []
    for j in range(obj.DocumentationLength()):
        doc_line = obj.Documentation(j)
        if doc_line:
            doc_line = doc_line.decode('utf8')
            docs.append(doc_line)
    docs = '\n'.join(docs).strip()
    return docs


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


class FbsField(object):
    pass


class FbsAttribute(object):
    def __init__(self):
        pass

    def __str__(self):
        return ''.format()


class FbsObject(object):
    def __init__(self,
                 name: str,
                 fields: Dict[str, FbsField],
                 is_struct: bool,
                 min_align: int,
                 bytesize: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._fields = fields
        self._is_struct = is_struct
        self._min_align = min_align
        self._bytesize = bytesize
        self._attrs = attrs
        self._docs = docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'fields': {},
            'is_struct': self._is_struct,
            'min_align': self._min_align,
            'bytesize': self._bytesize,
            'attrs': {},
            'docs': self._docs,
        }
        if self._fields:
            for k, v in self._fields.items():
                obj['fields'][k] = v
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj

    @property
    def name(self):
        return self._name

    @property
    def docs(self):
        return self._docs


class FbsRPCCall(object):
    def __init__(self,
                 name: str,
                 request: FbsObject,
                 response: FbsObject,
                 docs: str,
                 attrs: Dict[str, FbsAttribute]):
        self._name = name
        self._request = request
        self._response = response
        self._docs = docs
        self._attrs = attrs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'request': self._request.marshal() if self._request else None,
            'response': self._response.marshal() if self._response else None,
            'attrs': {},
            'docs': self._docs,
        }
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


class FbsService(object):
    def __init__(self,
                 name: str,
                 calls: Dict[str, FbsRPCCall],
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._calls = calls
        self._attrs = attrs
        self._docs = docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'calls': {},
            'attrs': {},
            'docs': self._docs,
        }
        if self._calls:
            for k, v in self._calls.items():
                obj['calls'][k] = v.marshal()
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


class FbsEnumValue(object):
    def __init__(self, name, value, docs):
        self._name = name
        self._value = value
        self._attrs = None
        self._docs = docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'attrs': {},
            'docs': self._docs,
        }
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


class FbsEnum(object):
    def __init__(self, name, values, is_union, underlying_type, attrs, docs):
        self._name = name
        self._values = values
        self._is_union = is_union
        self._underlying_type = underlying_type
        self._attrs = attrs
        self._docs = docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'attrs': {},
            'docs': self._docs,
        }
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


class FbsSchema(object):
    """
    """
    def __init__(self,
                 file_name: str,
                 file_sha256: str,
                 file_size: int,
                 root: _Schema,
                 objs: Dict[str, FbsObject],
                 enums: Dict[str, FbsEnum],
                 services: Dict[str, FbsService]):
        self._file_name = file_name
        self._file_sha256 = file_sha256
        self._file_size = file_size
        self._root = root
        self._objs = objs
        self._enums = enums
        self._services = services

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal(), width=140))

    def marshal(self):
        obj = {
            'schema': {
                'filename': os.path.basename(self._file_name),
                'sha256': self._file_sha256,
                'size': self._file_size,
                'objects': len(self._objs),
                'enums': len(self._enums),
                'services': len(self._services),
            },
            'enums': {},
            'objects': {},
            'services': {},
        }
        if self._enums:
            for k, v in self._enums.items():
                obj['enums'][k] = v.marshal()
        if self._objs:
            for k, v in self._objs.items():
                obj['objects'][k] = v.marshal()
        if self._services:
            for k, v in self._services.items():
                obj['services'][k] = v.marshal()
        return obj

    @staticmethod
    def load(filename):
        if not os.path.isfile(filename):
            raise RuntimeError('cannot open schema file {}'.format(filename))
        with open(filename, 'rb') as fd:
            data = fd.read()

        print('processing schema {} ({} bytes) ..'.format(filename, len(data)))
        root = _Schema.GetRootAsSchema(data, 0)

        objs = {}
        services = {}
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
                enum_value_docs = parse_docs(fbs_enum_value)
                enum_value = FbsEnumValue(name=enum_value_name, value=enum_value_value, docs=enum_value_docs)
                assert enum_value_name not in enum_values
                enum_values[enum_value_name] = enum_value

            enum = FbsEnum(name=enum_name, values=enum_values)
            assert enum_name not in enums
            enums[enum_name] = enum

        for i in range(root.ObjectsLength()):
            fbs_obj = root.Objects(i)
            obj_name = fbs_obj.Name()
            if obj_name:
                obj_name = obj_name.decode('utf8')
            obj_docs = parse_docs(fbs_obj)
            obj_attrs = parse_attr(fbs_obj)
            obj = FbsObject(name=obj_name,
                            fields=None,
                            is_struct=fbs_obj.IsStruct(),
                            min_align=fbs_obj.Minalign(),
                            bytesize=fbs_obj.Bytesize(),
                            attrs=obj_attrs,
                            docs=obj_docs)
            assert obj_name not in objs
            objs[obj_name] = obj

        for i in range(root.ServicesLength()):
            svc_obj = root.Services(i)

            svc_name = svc_obj.Name()
            if svc_name:
                svc_name = svc_name.decode('utf8')

            calls = {}
            for j in range(svc_obj.CallsLength()):
                fbs_call = svc_obj.Calls(j)

                call_name = fbs_call.Name()
                if call_name:
                    call_name = call_name.decode('utf8')

                fbs_call_req = fbs_call.Request()
                call_req_name = fbs_call_req.Name()
                if call_req_name:
                    call_req_name = call_req_name.decode('utf8')
                call_req_is_struct = fbs_call_req.IsStruct()
                call_req_min_align = fbs_call_req.Minalign()
                call_req_bytesize = fbs_call_req.Bytesize()
                call_req_docs = parse_docs(fbs_call_req)
                call_req_attrs = parse_attr(fbs_call_req)
                call_req = FbsObject(name=call_req_name,
                                     fields=None,
                                     is_struct=call_req_is_struct,
                                     min_align=call_req_min_align,
                                     bytesize=call_req_bytesize,
                                     attrs=call_req_attrs,
                                     docs=call_req_docs)

                fbs_call_resp = fbs_call.Response()
                call_resp_name = fbs_call_resp.Name()
                if call_resp_name:
                    call_resp_name = call_resp_name.decode('utf8')
                call_resp_is_struct = fbs_call_resp.IsStruct()
                call_resp_min_align = fbs_call_resp.Minalign()
                call_resp_bytesize = fbs_call_resp.Bytesize()
                call_resp_docs = parse_docs(fbs_call_resp)
                call_req_attrs = parse_attr(fbs_call_resp)
                call_resp = FbsObject(name=call_resp_name,
                                      fields=None,
                                      is_struct=call_resp_is_struct,
                                      min_align=call_resp_min_align,
                                      bytesize=call_resp_bytesize,
                                      attrs=call_req_attrs,
                                      docs=call_resp_docs)

                call_docs = parse_docs(fbs_call)
                call_attrs = parse_attr(fbs_call)
                call = FbsRPCCall(name=call_name,
                                  request=call_req,
                                  response=call_resp,
                                  docs=call_docs,
                                  attrs=call_attrs)
                assert call_name not in calls
                calls[call_name] = call

            docs = parse_docs(svc_obj)
            attrs = parse_attr(svc_obj)
            service = FbsService(name=svc_name, calls=calls, attrs=attrs, docs=docs)
            assert svc_name not in services
            services[svc_name] = service

        m = hashlib.sha256()
        m.update(data)

        schema = FbsSchema(file_name=filename,
                           file_size=len(data),
                           file_sha256=m.hexdigest(),
                           root=root,
                           objs=objs,
                           enums=enums,
                           services=services)
        return schema
