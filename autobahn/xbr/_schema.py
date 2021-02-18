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
from typing import Dict, Optional
from pathlib import Path

from zlmdb.flatbuffers.reflection.Schema import Schema as _Schema
from zlmdb.flatbuffers.reflection.BaseType import BaseType as _BaseType


class FbsType(object):
    """
    """

    # no type
    None_ = _BaseType.None_

    # ???
    UType = _BaseType.UType

    # scalar types
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

    SCALAR_TYPES = [_BaseType.Bool,
                    _BaseType.Byte,
                    _BaseType.UByte,
                    _BaseType.Short,
                    _BaseType.UShort,
                    _BaseType.Int,
                    _BaseType.UInt,
                    _BaseType.Long,
                    _BaseType.ULong,
                    _BaseType.Float,
                    _BaseType.Double,
                    _BaseType.String]

    # structured types
    Vector = _BaseType.Vector
    Obj = _BaseType.Obj
    Union = _BaseType.Union

    STRUCTURED_TYPES = [_BaseType.Vector,
                        _BaseType.Obj,
                        _BaseType.Union]

    FBS2PY = {
        _BaseType.None_: 'type(None)',
        _BaseType.UType: 'int',
        _BaseType.Bool: 'bool',
        _BaseType.Byte: 'bytes',
        _BaseType.UByte: 'int',
        _BaseType.Short: 'int',
        _BaseType.UShort: 'int',
        _BaseType.Int: 'int',
        _BaseType.UInt: 'int',
        _BaseType.Long: 'int',
        _BaseType.ULong: 'int',
        _BaseType.Float: 'float',
        _BaseType.Double: 'float',
        _BaseType.String: 'str',
        _BaseType.Vector: 'List',
        _BaseType.Obj: 'object',
        _BaseType.Union: 'Union',
    }

    FBS2FLAGS = {
        _BaseType.Bool: 'BoolFlags',
        _BaseType.Byte: 'Int8Flags',
        _BaseType.UByte: 'Uint8Flags',
        _BaseType.Short: 'Int16Flags',
        _BaseType.UShort: 'Uint16Flags',
        _BaseType.Int: 'Int32Flags',
        _BaseType.UInt: 'Uint32Flags',
        _BaseType.Long: 'Int64Flags',
        _BaseType.ULong: 'Uint64Flags',
        _BaseType.Float: 'Float32Flags',
        _BaseType.Double: 'Float64Flags',
    }

    FBS2PREPEND = {
        _BaseType.Bool: 'PrependBoolSlot',
        _BaseType.Byte: 'PrependInt8Slot',
        _BaseType.UByte: 'PrependUint8Slot',
        _BaseType.Short: 'PrependInt16Slot',
        _BaseType.UShort: 'PrependUint16Slot',
        _BaseType.Int: 'PrependInt32Slot',
        _BaseType.UInt: 'PrependUint32Slot',
        _BaseType.Long: 'PrependInt64Slot',
        _BaseType.ULong: 'PrependUint64Slot',
        _BaseType.Float: 'PrependFloat32Slot',
        _BaseType.Double: 'PrependFloat64Slot',
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

    def __init__(self, basetype: int, element: int, index: int):
        self._basetype = basetype
        self._element = element
        self._index = index

    @property
    def basetype(self):
        return self._basetype

    @property
    def element(self):
        return self._element

    @property
    def index(self):
        return self._index

    def map(self, language: str, attrs: Optional[Dict] = None, required: Optional[bool] = True) -> str:
        """

        :param language:
        :return:
        """
        if language == 'python':
            _mapped_type = None
            if self.basetype == FbsType.Vector:
                # vectors of uint8 are mapped to byte strings ..
                if self.element == FbsType.UByte:
                    if attrs and 'uuid' in attrs:
                        _mapped_type = 'uuid.UUID'
                    else:
                        _mapped_type = 'bytes'
                # .. whereas all other vectors are mapped to lists of the same element type
                else:
                    _mapped_type = 'List[{}]'.format(FbsType.FBS2PY[self.element])
            # FIXME: follow up processing of Unions (UType/Union)
            elif self.basetype in FbsType.SCALAR_TYPES + [FbsType.UType, FbsType.Union]:
                if self.basetype == FbsType.ULong and attrs and 'timestamp' in attrs:
                    _mapped_type = 'np.datetime64'
                else:
                    _mapped_type = FbsType.FBS2PY[self.basetype]
            else:
                raise NotImplementedError('FIXME: implement mapping of FlatBuffers type "{}" to Python in {}'.format(self.basetype, self.map))
            if required:
                return _mapped_type
            else:
                return 'Optional[{}]'.format(_mapped_type)
        else:
            raise RuntimeError('cannot map FlatBuffers type to target language "{}" in {}'.format(language, self.map))

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'basetype': self.FBS2STR.get(self._basetype, None),
            'element': self.FBS2STR.get(self._element, None),
            'index': self._index,
        }
        return obj


class FbsAttribute(object):
    def __init__(self):
        pass

    def __str__(self):
        return ''.format()


class FbsField(object):
    def __init__(self,
                 name: str,
                 type: FbsType,
                 id: int,
                 offset: int,
                 default_int: int,
                 default_real: float,
                 deprecated: bool,
                 required: bool,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._type = type
        self._id = id
        self._offset = offset
        self._default_int = default_int
        self._default_real = default_real
        self._deprecated = deprecated
        self._required = required
        self._attrs = attrs
        self._docs = docs

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def offset(self):
        return self._offset

    @property
    def default_int(self):
        return self._default_int

    @property
    def default_real(self):
        return self._default_real

    @property
    def deprecated(self):
        return self._deprecated

    @property
    def required(self):
        return self._required

    @property
    def attrs(self):
        return self._attrs

    @property
    def docs(self):
        return self._docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'type': self._type.marshal() if self._type else None,
            'id': self._id,
            'offset': self._offset,
            'default_int': self._default_int,
            'default_real': self._default_real,
            'deprecated': self._deprecated,
            'required': self._required,
            'attrs': {},
            'docs': self._docs,
        }
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


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


def parse_fields(obj):
    fields = {}
    fields_by_id = {}
    for j in range(obj.FieldsLength()):
        fbs_field = obj.Fields(j)

        field_name = fbs_field.Name()
        if field_name:
            field_name = field_name.decode('utf8')

        field_id = int(fbs_field.Id())

        fbs_field_type = fbs_field.Type()
        field_type = FbsType(basetype=fbs_field_type.BaseType(),
                             element=fbs_field_type.Element(),
                             index=fbs_field_type.Index())
        field = FbsField(name=field_name,
                         type=field_type,
                         id=field_id,
                         offset=fbs_field.Offset(),
                         default_int=fbs_field.DefaultInteger(),
                         default_real=fbs_field.DefaultReal(),
                         deprecated=fbs_field.Deprecated(),
                         required=fbs_field.Required(),
                         attrs=parse_attr(fbs_field),
                         docs=parse_docs(fbs_field))
        assert field_name not in fields, 'field "{}" with id "{}" already in fields {}'.format(field_name, field_id, sorted(fields.keys()))
        fields[field_name] = field
        assert field_id not in fields_by_id, 'field "{}" with id " {}" already in fields {}'.format(field_name, field_id, sorted(fields.keys()))
        fields_by_id[field_id] = field_name
    res = []
    for _, value in sorted(fields_by_id.items()):
        res.append(value)
    fields_by_id = res
    return fields, fields_by_id


def parse_calls(svc_obj):
    calls = {}
    calls_by_id = {}
    for j in range(svc_obj.CallsLength()):
        fbs_call = svc_obj.Calls(j)

        call_name = fbs_call.Name()
        if call_name:
            call_name = call_name.decode('utf8')

        # FIXME: schema reflection.RPCCall lacks "Id" (!)
        # call_id = int(fbs_call.Id())
        call_id = j

        fbs_call_req = fbs_call.Request()
        call_req_name = fbs_call_req.Name()
        if call_req_name:
            call_req_name = call_req_name.decode('utf8')
        call_req_is_struct = fbs_call_req.IsStruct()
        call_req_min_align = fbs_call_req.Minalign()
        call_req_bytesize = fbs_call_req.Bytesize()
        call_req_docs = parse_docs(fbs_call_req)
        call_req_attrs = parse_attr(fbs_call_req)
        call_req_fields, call_fields_by_id = parse_fields(fbs_call_req)
        call_req = FbsObject(name=call_req_name,
                             fields=call_req_fields,
                             fields_by_id=call_fields_by_id,
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
        call_resp_attrs = parse_attr(fbs_call_resp)
        call_resp_fields, call_resp_fields_by_id = parse_fields(fbs_call_resp)
        call_resp = FbsObject(name=call_resp_name,
                              fields=call_resp_fields,
                              fields_by_id=call_resp_fields_by_id,
                              is_struct=call_resp_is_struct,
                              min_align=call_resp_min_align,
                              bytesize=call_resp_bytesize,
                              attrs=call_resp_attrs,
                              docs=call_resp_docs)

        call_docs = parse_docs(fbs_call)
        call_attrs = parse_attr(fbs_call)
        call = FbsRPCCall(name=call_name,
                          id=call_id,
                          request=call_req,
                          response=call_resp,
                          docs=call_docs,
                          attrs=call_attrs)

        assert call_name not in calls, 'call "{}" with id "{}" already in calls {}'.format(call_name, call_id, sorted(calls.keys()))
        calls[call_name] = call
        assert call_id not in calls_by_id, 'call "{}" with id " {}" already in calls {}'.format(call_name, call_id, sorted(calls.keys()))
        calls_by_id[call_id] = call_name

    res = []
    for _, value in sorted(calls_by_id.items()):
        res.append(value)
    calls_by_id = res
    return calls, calls_by_id


class FbsObject(object):
    def __init__(self,
                 name: str,
                 fields: Dict[str, FbsField],
                 fields_by_id: Dict[int, str],
                 is_struct: bool,
                 min_align: int,
                 bytesize: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._fields = fields
        self._fields_by_id = fields_by_id
        self._is_struct = is_struct
        self._min_align = min_align
        self._bytesize = bytesize
        self._attrs = attrs
        self._docs = docs

    def map(self, language: str) -> str:
        if language == 'python':
            klass = self._name.split('.')[-1]
            return klass
        else:
            raise NotImplementedError()

    def map_import(self, language: str) -> str:
        if language == 'python':
            base = self._name.split('.')[-2]
            klass = self._name.split('.')[-1]
            return 'from {} import {}'.format(base, klass)
        else:
            raise NotImplementedError()

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields

    @property
    def fields_by_id(self):
        return self._fields_by_id

    @property
    def is_struct(self):
        return self._is_struct

    @property
    def min_align(self):
        return self._min_align

    @property
    def bytesize(self):
        return self._bytesize

    @property
    def attrs(self):
        return self._attrs

    @property
    def docs(self):
        return self._docs

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
                obj['fields'][k] = v.marshal() if v else None
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj

    @staticmethod
    def parse(fbs_obj):
        obj_name = fbs_obj.Name()
        if obj_name:
            obj_name = obj_name.decode('utf8')
        obj_docs = parse_docs(fbs_obj)
        obj_attrs = parse_attr(fbs_obj)
        obj_fields, obj_fields_by_id = parse_fields(fbs_obj)
        obj = FbsObject(name=obj_name,
                        fields=obj_fields,
                        fields_by_id=obj_fields_by_id,
                        is_struct=fbs_obj.IsStruct(),
                        min_align=fbs_obj.Minalign(),
                        bytesize=fbs_obj.Bytesize(),
                        attrs=obj_attrs,
                        docs=obj_docs)
        return obj


class FbsRPCCall(object):
    def __init__(self,
                 name: str,
                 id: int,
                 request: FbsObject,
                 response: FbsObject,
                 docs: str,
                 attrs: Dict[str, FbsAttribute]):
        self._name = name
        self._id = id
        self._request = request
        self._response = response
        self._docs = docs
        self._attrs = attrs

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def request(self):
        return self._request

    @property
    def response(self):
        return self._response

    @property
    def docs(self):
        return self._docs

    @property
    def attrs(self):
        return self._attrs

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
                 calls_by_id: Dict[int, str],
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._calls = calls
        self._calls_by_id = calls_by_id
        self._attrs = attrs
        self._docs = docs

    @property
    def name(self):
        return self._name

    @property
    def calls(self):
        return self._calls

    @property
    def calls_by_id(self):
        return self._calls_by_id

    @property
    def attrs(self):
        return self._attrs

    @property
    def docs(self):
        return self._docs

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
        self._attrs = {}
        self._docs = docs

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def attrs(self):
        return self._attrs

    @property
    def docs(self):
        return self._docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'attrs': self._attrs,
            'docs': self._docs,
            'value': self._value,
        }
        if self._attrs:
            for k, v in self._attrs.items():
                obj['attrs'][k] = v
        return obj


class FbsEnum(object):
    """
    FlatBuffers enum type.
    """
    def __init__(self,
                 name: str,
                 values: Dict[str, FbsEnumValue],
                 is_union: bool,
                 underlying_type: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._name = name
        self._values = values
        self._is_union = is_union

        # zlmdb.flatbuffers.reflection.Type.Type
        self._underlying_type = underlying_type
        self._attrs = attrs
        self._docs = docs

    @property
    def name(self):
        return self._name

    @property
    def values(self):
        return self._values

    @property
    def is_union(self):
        return self._is_union

    @property
    def underlying_type(self):
        return self._underlying_type

    @property
    def attrs(self):
        return self._attrs

    @property
    def docs(self):
        return self._docs

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self):
        obj = {
            'name': self._name,
            'values': {},
            'is_union': self._is_union,
            'underlying_type': FbsType.FBS2STR.get(self._underlying_type, None),
            'attrs': {},
            'docs': self._docs,
        }
        if self._values:
            for k, v in self._values.items():
                obj['values'][k] = v.marshal()
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
                 file_ident: str,
                 file_ext: str,
                 root_table: FbsObject,
                 root: _Schema,
                 objs: Dict[str, FbsObject],
                 enums: Dict[str, FbsEnum],
                 services: Dict[str, FbsService]):
        """

        :param file_name:
        :param file_sha256:
        :param file_size:
        :param file_ident:
        :param file_ext:
        :param root_table:
        :param root:
        :param objs:
        :param enums:
        :param services:
        """
        self._file_name = file_name
        self._file_sha256 = file_sha256
        self._file_size = file_size
        self._file_ident = file_ident
        self._file_ext = file_ext
        self._root_table = root_table
        self._root = root
        self._objs = objs
        self._enums = enums
        self._services = services

    @property
    def file_name(self):
        return self._file_name

    @property
    def file_sha256(self):
        return self._file_sha256

    @property
    def file_size(self):
        return self._file_size

    @property
    def file_ident(self):
        return self._file_ident

    @property
    def file_ext(self):
        return self._file_ext

    @property
    def root_table(self):
        return self._root_table

    @property
    def root(self):
        return self._root

    @property
    def objs(self):
        return self._objs

    @property
    def enums(self):
        return self._enums

    @property
    def services(self):
        return self._services

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal(), width=255))

    def marshal(self) -> Dict[str, object]:
        """

        :return:
        """
        obj = {
            'schema': {
                'ident': self._file_ident,
                'ext': self._file_ext,
                'name': os.path.basename(self._file_name) if self._file_name else None,
                'sha256': self._file_sha256,
                'size': self._file_size,
                'objects': len(self._objs),
                'enums': len(self._enums),
                'services': len(self._services),
            },
            'root_table': self._root_table.marshal() if self._root_table else None,
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
    def load(filename) -> object:
        """

        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            raise RuntimeError('cannot open schema file {}'.format(filename))
        with open(filename, 'rb') as fd:
            data = fd.read()

        print('processing schema {} ({} bytes) ..'.format(filename, len(data)))
        root = _Schema.GetRootAsSchema(data, 0)

        file_ident = root.FileIdent()
        if file_ident is not None:
            file_ident = file_ident.decode('utf8')

        file_ext = root.FileExt()
        if file_ext is not None:
            file_ext = file_ext.decode('utf8')

        root_table = root.RootTable()
        if root_table is not None:
            root_table = FbsObject.parse(root_table)

        objs = {}
        services = {}
        enums = {}

        for i in range(root.EnumsLength()):
            fbs_enum = root.Enums(i)

            enum_name = fbs_enum.Name()
            if enum_name:
                enum_name = enum_name.decode('utf8')

            enum_underlying_type = fbs_enum.UnderlyingType()

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

            enum = FbsEnum(name=enum_name,
                           values=enum_values,
                           is_union=fbs_enum.IsUnion(),
                           underlying_type=enum_underlying_type,
                           attrs=parse_attr(fbs_enum),
                           docs=parse_docs(fbs_enum))
            assert enum_name not in enums
            enums[enum_name] = enum

        for i in range(root.ObjectsLength()):
            fbs_obj = root.Objects(i)
            obj = FbsObject.parse(fbs_obj)
            assert obj.name not in objs
            objs[obj.name] = obj

        for i in range(root.ServicesLength()):
            svc_obj = root.Services(i)

            svc_name = svc_obj.Name()
            if svc_name:
                svc_name = svc_name.decode('utf8')

            docs = parse_docs(svc_obj)
            attrs = parse_attr(svc_obj)
            calls, calls_by_id = parse_calls(svc_obj)

            service = FbsService(name=svc_name, calls=calls, calls_by_id=calls_by_id, attrs=attrs, docs=docs)
            assert svc_name not in services
            services[svc_name] = service

        m = hashlib.sha256()
        m.update(data)

        schema = FbsSchema(file_name=filename,
                           file_size=len(data),
                           file_sha256=m.hexdigest(),
                           file_ident=file_ident,
                           file_ext=file_ext,
                           root_table=root_table,
                           root=root,
                           objs=objs,
                           enums=enums,
                           services=services)
        return schema


class FbsRepository(object):
    """
    """

    def __init__(self):
        self._schemata = {}

        # Dict[str, FbsObject]
        self._objs = {}

        # Dict[str, FbsEnum]
        self._enums = {}

        # Dict[str, FbsService]
        self._services = {}

    def summary(self, keys=False):
        if keys:
            return {
                'schemata': sorted(self._schemata.keys()),
                'objs': sorted(self._objs.keys()),
                'enums': sorted(self._enums.keys()),
                'services': sorted(self._services.keys()),
            }
        else:
            return {
                'schemata': len(self._schemata),
                'objs': len(self._objs),
                'enums': len(self._enums),
                'services': len(self._services),
            }

    @property
    def objs(self):
        return self._objs

    @property
    def enums(self):
        return self._enums

    @property
    def services(self):
        return self._services

    def load(self, dirname) -> object:
        if not os.path.isdir(dirname):
            raise RuntimeError('cannot open schema directory {}'.format(dirname))

        found = []
        for path in Path(dirname).rglob('*.bfbs'):
            fn = os.path.abspath(os.path.join(dirname, path.name))
            if fn not in self._schemata:
                found.append(fn)
            else:
                print('duplicate schema: {} already loaded'.format(fn))

        for fn in found:
            schema = FbsSchema.load(fn)

            # load enum types
            for enum in schema.enums.values():
                if enum.name in self._enums:
                    print('duplicate enum for name "{}"'.format(enum.name))
                else:
                    self._enums[enum.name] = enum

            # load object types
            for obj in schema.objs.values():
                if obj.name in self._objs:
                    print('duplicate object for name "{}"'.format(obj.name))
                else:
                    self._objs[obj.name] = obj

            # load service definitions ("APIs")
            for svc in schema.services.values():
                if svc.name in self._services:
                    print('duplicate service for name "{}"'.format(svc.name))
                else:
                    self._services[svc.name] = svc

            self._schemata[fn] = schema
