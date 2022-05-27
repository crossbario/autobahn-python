###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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
from typing import Dict, List, Optional
from pathlib import Path

from zlmdb.flatbuffers.reflection.Schema import Schema as _Schema
from zlmdb.flatbuffers.reflection.BaseType import BaseType as _BaseType


class FbsType(object):
    """
    Flatbuffers type.

    See: https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs
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

    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 basetype: int,
                 element: int,
                 index: int,
                 objtype: Optional[str] = None):
        self._repository = repository
        self._schema = schema
        self._basetype = basetype
        self._element = element
        self._index = index
        self._objtype = objtype

    @property
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

    @property
    def basetype(self):
        """
        Flatbuffers base type.

        :return:
        """
        return self._basetype

    @property
    def element(self):
        """
        Only if basetype == Vector or basetype == Array.

        :return:
        """
        return self._element

    @property
    def index(self):
        """
        If basetype == Object, index into "objects".

        :return:
        """
        return self._index

    @property
    def objtype(self):
        """
        If basetype == Object, fully qualified object type name.

        :return:
        """
        if self._basetype == FbsType.Obj:
            if self._objtype is None:
                self._objtype = self._schema.objs_by_id[self._index].name
                # print('filled in missing objtype "{}" for type index {} in object {}'.format(self._objtype, self._index, self))
        return self._objtype

    def map(self, language: str, attrs: Optional[Dict] = None, required: Optional[bool] = True,
            objtype_as_string: bool = False) -> str:
        """

        :param language:
        :param attrs:
        :param required:
        :param objtype_as_string:
        :return:
        """
        if language == 'python':
            _mapped_type = None

            if self.basetype == FbsType.Vector:
                # vectors of uint8 are mapped to byte strings
                if self.element == FbsType.UByte:
                    if attrs and 'uuid' in attrs:
                        _mapped_type = 'uuid.UUID'
                    else:
                        _mapped_type = 'bytes'
                # whereas all other vectors are mapped to list of the same element type
                else:
                    if self.objtype:
                        # FIXME
                        _mapped_type = 'List[{}]'.format(self.objtype.split('.')[-1])
                        # _mapped_type = 'List[{}.{}]'.format(self._repository.render_to_basemodule, self.objtype)
                    else:
                        _mapped_type = 'List[{}]'.format(FbsType.FBS2PY[self.element])

            elif self.basetype == FbsType.Obj:
                if self.objtype:
                    # FIXME
                    _mapped_type = self.objtype.split('.')[-1]
                    # _mapped_type = '{}.{}'.format(self._repository.render_to_basemodule, self.objtype)
                else:
                    _mapped_type = 'List[{}]'.format(FbsType.FBS2PY[self.element])

            elif self.basetype in FbsType.SCALAR_TYPES + [FbsType.UType, FbsType.Union]:
                # FIXME: follow up processing of Unions (UType/Union)
                if self.basetype == FbsType.ULong and attrs and 'timestamp' in attrs:
                    _mapped_type = 'np.datetime64'
                else:
                    _mapped_type = FbsType.FBS2PY[self.basetype]

            else:
                raise NotImplementedError('FIXME: implement mapping of FlatBuffers type "{}" to Python in {}'.format(self.basetype, self.map))

            if objtype_as_string and self.basetype == FbsType.Obj:
                # for object types, use 'TYPE' rather than TYPE so that the type reference
                # does not depend on type declaration order within a single file
                # https://peps.python.org/pep-0484/#forward-references
                if required:
                    return "'{}'".format(_mapped_type)
                else:
                    return "Optional['{}']".format(_mapped_type)
            else:
                if required:
                    return '{}'.format(_mapped_type)
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
            'objtype': self._objtype,
        }
        return obj


class FbsAttribute(object):
    def __init__(self):
        pass

    def __str__(self):
        return ''.format()


class FbsField(object):
    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
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
        self._repository = repository
        self._schema = schema
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
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
            doc_line = doc_line.decode('utf8').strip()
            docs.append(doc_line)
    # docs = '\n'.join(docs).strip()
    docs = ' '.join(docs).strip()
    return docs


def parse_fields(repository, schema, obj, objs_lst=None):
    fields_by_name = {}
    fields_by_id = []
    for j in range(obj.FieldsLength()):
        fbs_field = obj.Fields(j)

        field_name = fbs_field.Name()
        if field_name:
            field_name = field_name.decode('utf8')

        field_id = int(fbs_field.Id())
        fbs_field_type = fbs_field.Type()

        # FIXME
        _objtype = None
        if fbs_field_type.Index() >= 0:
            if len(objs_lst) > fbs_field_type.Index():
                _obj = objs_lst[fbs_field_type.Index()]
                _objtype = _obj.name

        field_type = FbsType(repository=repository,
                             schema=schema,
                             basetype=fbs_field_type.BaseType(),
                             element=fbs_field_type.Element(),
                             index=fbs_field_type.Index(),
                             objtype=_objtype)
        field = FbsField(repository=repository,
                         schema=schema,
                         name=field_name,
                         type=field_type,
                         id=field_id,
                         offset=fbs_field.Offset(),
                         default_int=fbs_field.DefaultInteger(),
                         default_real=fbs_field.DefaultReal(),
                         deprecated=fbs_field.Deprecated(),
                         required=fbs_field.Required(),
                         attrs=parse_attr(fbs_field),
                         docs=parse_docs(fbs_field))
        assert field_name not in fields_by_name, 'field "{}" with id "{}" already in fields {}'.format(field_name, field_id, sorted(fields_by_name.keys()))
        fields_by_name[field_name] = field
        assert field_id not in fields_by_id, 'field "{}" with id " {}" already in fields {}'.format(field_name, field_id, sorted(fields_by_id.keys()))
        fields_by_id.append(field)
    return fields_by_name, fields_by_id


def parse_calls(repository, schema, svc_obj, objs_lst=None):
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
        call_req_fields, call_fields_by_id = parse_fields(repository, schema, fbs_call_req, objs_lst=objs_lst)
        call_req = FbsObject(repository=repository,
                             schema=schema,
                             name=call_req_name,
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
        call_resp_fields, call_resp_fields_by_id = parse_fields(repository, schema, fbs_call_resp, objs_lst=objs_lst)
        call_resp = FbsObject(repository=repository,
                              schema=schema,
                              name=call_resp_name,
                              fields=call_resp_fields,
                              fields_by_id=call_resp_fields_by_id,
                              is_struct=call_resp_is_struct,
                              min_align=call_resp_min_align,
                              bytesize=call_resp_bytesize,
                              attrs=call_resp_attrs,
                              docs=call_resp_docs)

        call_docs = parse_docs(fbs_call)
        call_attrs = parse_attr(fbs_call)
        call = FbsRPCCall(repository=repository,
                          schema=schema,
                          name=call_name,
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
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 name: str,
                 fields: Dict[str, FbsField],
                 fields_by_id: List[FbsField],
                 is_struct: bool,
                 min_align: int,
                 bytesize: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._repository = repository
        self._schema = schema
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
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
    def parse(repository, schema, fbs_obj, objs_lst=None):
        obj_name = fbs_obj.Name()
        if obj_name:
            obj_name = obj_name.decode('utf8')
        obj_docs = parse_docs(fbs_obj)
        obj_attrs = parse_attr(fbs_obj)

        fields_by_name, fields_by_id = parse_fields(repository, schema, fbs_obj, objs_lst=objs_lst)
        # print('ok, parsed fields in object "{}": {}'.format(obj_name, fields_by_name))
        obj = FbsObject(repository=repository,
                        schema=schema,
                        name=obj_name,
                        fields=fields_by_name,
                        fields_by_id=fields_by_id,
                        is_struct=fbs_obj.IsStruct(),
                        min_align=fbs_obj.Minalign(),
                        bytesize=fbs_obj.Bytesize(),
                        attrs=obj_attrs,
                        docs=obj_docs)
        return obj


class FbsRPCCall(object):
    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 name: str,
                 id: int,
                 request: FbsObject,
                 response: FbsObject,
                 docs: str,
                 attrs: Dict[str, FbsAttribute]):
        self._repository = repository
        self._schema = schema
        self._name = name
        self._id = id
        self._request = request
        self._response = response
        self._docs = docs
        self._attrs = attrs

    @property
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 name: str,
                 calls: Dict[str, FbsRPCCall],
                 calls_by_id: List[FbsRPCCall],
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._repository = repository
        self._schema = schema
        self._name = name
        self._calls = calls
        self._calls_by_id = calls_by_id
        self._attrs = attrs
        self._docs = docs

    @property
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 name,
                 value,
                 docs):
        """

        :param repository:
        :param name:
        :param value:
        :param docs:
        """
        self._repository = repository
        self._schema = schema
        self._name = name
        self._value = value
        self._attrs = {}
        self._docs = docs

    @property
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 name: str,
                 values: Dict[str, FbsEnumValue],
                 is_union: bool,
                 underlying_type: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._repository = repository
        self._schema = schema
        self._name = name
        self._values = values
        self._is_union = is_union

        # zlmdb.flatbuffers.reflection.Type.Type
        self._underlying_type = underlying_type
        self._attrs = attrs
        self._docs = docs

    @property
    def repository(self):
        return self._repository

    @property
    def schema(self):
        return self._schema

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
                 repository: 'FbsRepository',
                 file_name: str,
                 file_sha256: str,
                 file_size: int,
                 file_ident: str,
                 file_ext: str,
                 root_table: FbsObject,
                 root: _Schema,
                 objs: Optional[Dict[str, FbsObject]] = None,
                 objs_by_id: Optional[List[FbsObject]] = None,
                 enums: Optional[Dict[str, FbsEnum]] = None,
                 enums_by_id: Optional[List[FbsEnum]] = None,
                 services: Optional[Dict[str, FbsService]] = None,
                 services_by_id: Optional[List[FbsService]] = None):
        """

        :param repository:
        :param file_name:
        :param file_sha256:
        :param file_size:
        :param file_ident:
        :param file_ext:
        :param root_table:
        :param root:
        :param objs:
        :param objs_by_id:
        :param enums:
        :param enums_by_id:
        :param services:
        :param services_by_id:
        """
        self._repository = repository
        self._file_name = file_name
        self._file_sha256 = file_sha256
        self._file_size = file_size
        self._file_ident = file_ident
        self._file_ext = file_ext
        self._root_table = root_table
        self._root = root
        self._objs = objs
        self._objs_by_id = objs_by_id
        self._enums = enums
        self._enums_by_id = enums_by_id
        self._services = services
        self._services_by_id = services_by_id

    @property
    def repository(self):
        return self._repository

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
    def objs_by_id(self):
        return self._objs_by_id

    @property
    def enums(self):
        return self._enums

    @property
    def enums_by_id(self):
        return self._enums_by_id

    @property
    def services(self):
        return self._services

    @property
    def services_by_id(self):
        return self._services_by_id

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
    def load(repository, filename) -> 'FbsSchema':
        """

        :param repository:
        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            raise RuntimeError('cannot open schema file {}'.format(filename))
        with open(filename, 'rb') as fd:
            data = fd.read()
        m = hashlib.sha256()
        m.update(data)
        print('processing schema file "{}" ({} bytes, SHA256 0x{}) ..'.format(filename, len(data), m.hexdigest()))

        # get root object in Flatbuffers reflection schema
        # see: https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs
        root = _Schema.GetRootAsSchema(data, 0)

        file_ident = root.FileIdent()
        if file_ident is not None:
            file_ident = file_ident.decode('utf8')

        file_ext = root.FileExt()
        if file_ext is not None:
            file_ext = file_ext.decode('utf8')

        root_table = root.RootTable()
        if root_table is not None:
            root_table = FbsObject.parse(repository, root_table)

        schema = FbsSchema(repository=repository,
                           file_name=filename,
                           file_size=len(data),
                           file_sha256=m.hexdigest(),
                           file_ident=file_ident,
                           file_ext=file_ext,
                           root_table=root_table,
                           root=root)

        # enum types from the schema by name and by index
        enums = {}
        enums_by_id = []
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
                enum_value = FbsEnumValue(repository=repository,
                                          name=enum_value_name,
                                          value=enum_value_value,
                                          docs=enum_value_docs)
                assert enum_value_name not in enum_values
                enum_values[enum_value_name] = enum_value

            enum = FbsEnum(repository=repository,
                           schema=schema,
                           name=enum_name,
                           values=enum_values,
                           is_union=fbs_enum.IsUnion(),
                           underlying_type=enum_underlying_type,
                           attrs=parse_attr(fbs_enum),
                           docs=parse_docs(fbs_enum))
            assert enum_name not in enums
            enums[enum_name] = enum
            enums_by_id.append(enum)
        schema._enums = enums
        schema._enums_by_id = enums_by_id

        # type objects (structs and tables) from the schema by name and by index
        objs = {}
        objs_by_id = []
        for i in range(root.ObjectsLength()):
            fbs_obj = root.Objects(i)
            obj = FbsObject.parse(repository, schema, fbs_obj, objs_lst=objs_by_id)
            assert obj.name not in objs
            objs[obj.name] = obj
            objs_by_id.append(obj)
            print('ok, processed schema object "{}"'.format(obj.name))
        schema._objs = objs
        schema._objs_by_id = objs_by_id

        # service type objects (interfaces) from the schema by name and by index
        services = {}
        services_by_id = []
        for i in range(root.ServicesLength()):
            svc_obj = root.Services(i)

            svc_name = svc_obj.Name()
            if svc_name:
                svc_name = svc_name.decode('utf8')

            docs = parse_docs(svc_obj)
            attrs = parse_attr(svc_obj)
            calls, calls_by_id = parse_calls(repository, schema, svc_obj, objs_lst=objs_by_id)

            service = FbsService(repository=repository,
                                 schema=schema,
                                 name=svc_name,
                                 calls=calls,
                                 calls_by_id=calls_by_id,
                                 attrs=attrs,
                                 docs=docs)
            assert svc_name not in services
            services[svc_name] = service
            services_by_id.append(service)
        schema._services = services
        schema._services_by_id = services_by_id

        return schema


class FbsRepository(object):
    """

    https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs
    """

    def __init__(self, render_to_basemodule):
        self._render_to_basemodule = render_to_basemodule

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
    def render_to_basemodule(self):
        return self._render_to_basemodule

    @property
    def objs(self):
        return self._objs

    @property
    def enums(self):
        return self._enums

    @property
    def services(self):
        return self._services

    def load(self, filename: str):
        """
        Load and add all schemata from Flatbuffers binary schema files (`*.bfbs`)
        found in the given directory. Alternatively, a path to a single schema file
        can be provided.

        :param filename: Filesystem path of a directory or single file from which to
            load and add Flatbuffers schemata.
        """
        load_from_filenames = []
        if os.path.isdir(filename):
            for path in Path(filename).rglob('*.bfbs'):
                fn = os.path.join(filename, path.name)
                if fn not in self._schemata:
                    load_from_filenames.append(fn)
                else:
                    print('duplicate schema file skipped ("{}" already loaded)'.format(fn))
        elif os.path.isfile(filename):
            if filename not in self._schemata:
                load_from_filenames.append(filename)
            else:
                print('duplicate schema file skipped ("{}" already loaded)'.format(filename))
        else:
            raise RuntimeError('cannot open schema file or directory: "{}"'.format(filename))

        # iterate over all schema files found
        for fn in load_from_filenames:
            # load this schema file
            schema: FbsSchema = FbsSchema.load(self, fn)

            # add enum types to repository by name
            for enum in schema.enums.values():
                if enum.name in self._enums:
                    print('duplicate enum for name "{}"'.format(enum.name))
                else:
                    self._enums[enum.name] = enum

            # add object types
            for obj in schema.objs.values():
                if obj.name in self._objs:
                    print('duplicate object for name "{}"'.format(obj.name))
                else:
                    self._objs[obj.name] = obj

            # add service definitions ("APIs")
            for svc in schema.services.values():
                if svc.name in self._services:
                    print('duplicate service for name "{}"'.format(svc.name))
                else:
                    self._services[svc.name] = svc

            self._schemata[fn] = schema
