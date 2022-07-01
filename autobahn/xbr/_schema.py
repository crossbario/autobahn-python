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
import json
import os
import io
import pprint
import hashlib
import textwrap
from pathlib import Path
from pprint import pformat
from typing import Union, Dict, List, Optional, IO, Any, Tuple
from collections.abc import Sequence

# FIXME
# https://github.com/google/yapf#example-as-a-module
from yapf.yapflib.yapf_api import FormatCode

import txaio
from autobahn.wamp.exception import InvalidPayload
from autobahn.util import hlval

from zlmdb.flatbuffers.reflection.Schema import Schema as _Schema
from zlmdb.flatbuffers.reflection.BaseType import BaseType as _BaseType
from zlmdb.flatbuffers.reflection.Field import Field


class FbsType(object):
    """
    Flatbuffers type.

    See: https://github.com/google/flatbuffers/blob/11a19887053534c43f73e74786b46a615ecbf28e/reflection/reflection.fbs#L33
    """

    __slots__ = ('_repository', '_schema', '_basetype', '_element', '_index', '_objtype', '_elementtype')

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

    FBS2PY_TYPE = {
        _BaseType.UType: int,
        _BaseType.Bool: bool,
        _BaseType.Byte: int,
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
        _BaseType.Vector: list,
        _BaseType.Obj: dict,
        # _BaseType.Union: 'Union',
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
                 objtype: Optional[str] = None,
                 elementtype: Optional[str] = None):
        self._repository = repository
        self._schema = schema
        self._basetype = basetype
        self._element = element
        self._elementtype = elementtype
        self._index = index
        self._objtype = objtype

    @property
    def repository(self) -> 'FbsRepository':
        return self._repository

    @property
    def schema(self) -> 'FbsSchema':
        return self._schema

    @property
    def basetype(self) -> int:
        """
        Flatbuffers base type.

        :return:
        """
        return self._basetype

    @property
    def element(self) -> int:
        """
        Only if basetype == Vector

        :return:
        """
        return self._element

    @property
    def index(self) -> int:
        """
        If basetype == Object, index into "objects".
        If base_type == Union, UnionType, or integral derived from an enum, index into "enums".
        If base_type == Vector && element == Union or UnionType.

        :return:
        """
        return self._index

    @property
    def elementtype(self) -> Optional[str]:
        """
        If basetype == Vector, fully qualified element type name.

        :return:
        """
        # lazy-resolve of element type index to element type name. this is important (!)
        # to decouple from loading order of type objects
        if self._basetype == FbsType.Vector and self._elementtype is None:
            if self._element == FbsType.Obj:
                self._elementtype = self._schema.objs_by_id[self._index].name
                # print('filled in missing elementtype "{}" for element type index {} in vector'.format(self._elementtype, self._index))
            else:
                assert False, 'FIXME'
        return self._elementtype

    @property
    def objtype(self) -> Optional[str]:
        """
        If basetype == Object, fully qualified object type name.

        :return:
        """
        # lazy-resolve of object type index to object type name. this is important (!)
        # to decouple from loading order of type objects
        if self._basetype == FbsType.Obj and self._objtype is None:
            self._objtype = self._schema.objs_by_id[self._index].name
            # print('filled in missing objtype "{}" for object type index {} in object'.format(self._objtype, self._index))
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
                raise NotImplementedError(
                    'FIXME: implement mapping of FlatBuffers type "{}" to Python in {}'.format(self.basetype, self.map))

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

    def __str__(self) -> str:
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self) -> Dict[str, Any]:
        # important: use properties, not private object attribute access (!)
        obj = {
            'basetype': self.FBS2STR.get(self.basetype, None),
            'element': self.FBS2STR.get(self.element, None),
            'index': self.index,
            'objtype': self.objtype,
        }
        return obj


class FbsAttribute(object):
    def __init__(self):
        pass

    def __str__(self):
        return ''.format()


class FbsField(object):
    __slots__ = ('_repository', '_schema', '_name', '_type', '_id', '_offset', '_default_int',
                 '_default_real', '_deprecated', '_required', '_attrs', '_docs')

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
    def repository(self) -> 'FbsRepository':
        return self._repository

    @property
    def schema(self) -> 'FbsSchema':
        return self._schema

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> FbsType:
        return self._type

    @property
    def id(self) -> int:
        return self._id

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def default_int(self) -> int:
        return self._default_int

    @property
    def default_real(self) -> float:
        return self._default_real

    @property
    def deprecated(self) -> bool:
        return self._deprecated

    @property
    def required(self) -> bool:
        return self._required

    @property
    def attrs(self) -> Dict[str, FbsAttribute]:
        return self._attrs

    @property
    def docs(self) -> str:
        return self._docs

    def __str__(self) -> str:
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self) -> Dict[str, Any]:
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

    # table Object {  // Used for both tables and structs.
    # ...
    #     fields:[Field] (required);  // Sorted.
    # ...
    # }
    # https://github.com/google/flatbuffers/blob/11a19887053534c43f73e74786b46a615ecbf28e/reflection/reflection.fbs#L91

    fields_by_name = {}

    # the type index of a field is stored in ``fbs_field.Id()``, whereas the index of the field
    # within the list of fields is different (!) because that list is alphabetically sorted (!).
    # thus, we need to fill this map to recover the type index ordered list of fields
    field_id_to_name = {}

    for j in range(obj.FieldsLength()):
        fbs_field: Field = obj.Fields(j)

        field_name = fbs_field.Name()
        if field_name:
            field_name = field_name.decode('utf8')

        field_id = int(fbs_field.Id())

        # IMPORTANT: this is NOT true, since j is according to sort-by-name
        # assert field_id == j

        # instead, maintain this map to recover sort-by-position order later
        field_id_to_name[field_id] = field_name

        fbs_field_type = fbs_field.Type()

        # we use lazy-resolve for this property
        _objtype = None

        # # FIXME
        # _objtype = None
        # if fbs_field_type.Index() >= 0:
        #     if len(objs_lst) > fbs_field_type.Index():
        #         _obj = objs_lst[fbs_field_type.Index()]
        #         _objtype = _obj.name

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
        assert field_name not in fields_by_name, 'field "{}" with id "{}" already in fields {}'.format(field_name,
                                                                                                       field_id,
                                                                                                       sorted(fields_by_name.keys()))
        fields_by_name[field_name] = field

    # recover the type index ordered list of fields
    fields_by_id = []
    for i in range(len(fields_by_name)):
        fields_by_id.append(fields_by_name[field_id_to_name[i]])

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
        call_req_declaration_file = fbs_call_req.DeclarationFile()
        if call_req_declaration_file:
            call_req_declaration_file = call_req_declaration_file.decode('utf8')
        call_req_is_struct = fbs_call_req.IsStruct()
        call_req_min_align = fbs_call_req.Minalign()
        call_req_bytesize = fbs_call_req.Bytesize()
        call_req_docs = parse_docs(fbs_call_req)
        call_req_attrs = parse_attr(fbs_call_req)
        call_req_fields, call_fields_by_id = parse_fields(repository, schema, fbs_call_req, objs_lst=objs_lst)
        call_req = FbsObject(repository=repository,
                             schema=schema,
                             declaration_file=call_req_declaration_file,
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
        call_resp_declaration_file = fbs_call_resp.DeclarationFile()
        if call_resp_declaration_file:
            call_resp_declaration_file = call_resp_declaration_file.decode('utf8')
        call_resp_is_struct = fbs_call_resp.IsStruct()
        call_resp_min_align = fbs_call_resp.Minalign()
        call_resp_bytesize = fbs_call_resp.Bytesize()
        call_resp_docs = parse_docs(fbs_call_resp)
        call_resp_attrs = parse_attr(fbs_call_resp)
        call_resp_fields, call_resp_fields_by_id = parse_fields(repository, schema, fbs_call_resp, objs_lst=objs_lst)
        call_resp = FbsObject(repository=repository,
                              schema=schema,
                              declaration_file=call_resp_declaration_file,
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

        assert call_name not in calls, 'call "{}" with id "{}" already in calls {}'.format(call_name, call_id,
                                                                                           sorted(calls.keys()))
        calls[call_name] = call
        assert call_id not in calls_by_id, 'call "{}" with id " {}" already in calls {}'.format(call_name, call_id,
                                                                                                sorted(calls.keys()))
        calls_by_id[call_id] = call_name

    res = []
    for _, value in sorted(calls_by_id.items()):
        res.append(value)
    calls_by_id = res
    return calls, calls_by_id


class FbsObject(object):
    __slots__ = ('_repository', '_schema', '_declaration_file', '_name', '_fields', '_fields_by_id',
                 '_is_struct', '_min_align', '_bytesize', '_attrs', '_docs')

    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 declaration_file: str,
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
        self._declaration_file = declaration_file
        self._name = name
        self._fields = fields
        self._fields_by_id = fields_by_id
        self._is_struct = is_struct
        self._min_align = min_align
        self._bytesize = bytesize
        self._attrs = attrs
        self._docs = docs

    def map(self, language: str, required: Optional[bool] = True, objtype_as_string: bool = False) -> str:
        if language == 'python':
            klass = self._name.split('.')[-1]
            if objtype_as_string:
                # for object types, use 'TYPE' rather than TYPE so that the type reference
                # does not depend on type declaration order within a single file
                # https://peps.python.org/pep-0484/#forward-references
                if required:
                    return "'{}'".format(klass)
                else:
                    return "Optional['{}']".format(klass)
            else:
                if required:
                    return '{}'.format(klass)
                else:
                    return 'Optional[{}]'.format(klass)
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
    def repository(self) -> 'FbsRepository':
        return self._repository

    @property
    def schema(self) -> 'FbsSchema':
        return self._schema

    @property
    def declaration_file(self) -> str:
        return self._declaration_file

    @property
    def name(self) -> str:
        return self._name

    @property
    def fields(self) -> Dict[str, FbsField]:
        return self._fields

    @property
    def fields_by_id(self) -> List[FbsField]:
        return self._fields_by_id

    @property
    def is_struct(self) -> bool:
        return self._is_struct

    @property
    def min_align(self) -> int:
        return self._min_align

    @property
    def bytesize(self) -> int:
        return self._bytesize

    @property
    def attrs(self) -> Dict[str, FbsAttribute]:
        return self._attrs

    @property
    def docs(self) -> str:
        return self._docs

    def __str__(self) -> str:
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    def marshal(self) -> Dict[str, Any]:
        obj = {
            'name': self._name,
            'declaration_file': self._declaration_file,
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
        obj_declaration_file = fbs_obj.DeclarationFile()
        if obj_declaration_file:
            obj_declaration_file = obj_declaration_file.decode('utf8')
        obj_docs = parse_docs(fbs_obj)
        obj_attrs = parse_attr(fbs_obj)

        fields_by_name, fields_by_id = parse_fields(repository, schema, fbs_obj, objs_lst=objs_lst)
        # print('ok, parsed fields in object "{}": {}'.format(obj_name, fields_by_name))
        obj = FbsObject(repository=repository,
                        schema=schema,
                        declaration_file=obj_declaration_file,
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
                 declaration_file: str,
                 name: str,
                 calls: Dict[str, FbsRPCCall],
                 calls_by_id: List[FbsRPCCall],
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._repository = repository
        self._schema = schema
        self._declaration_file = declaration_file
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
    def declaration_file(self):
        return self._declaration_file

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
            'declaration_file': self._declaration_file,
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
                 name: str,
                 id: int,
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
        self._id = id
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
    def id(self):
        return self._id

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
            'id': self._id,
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

    See https://github.com/google/flatbuffers/blob/11a19887053534c43f73e74786b46a615ecbf28e/reflection/reflection.fbs#L61
    """

    def __init__(self,
                 repository: 'FbsRepository',
                 schema: 'FbsSchema',
                 declaration_file: str,
                 name: str,
                 id: int,
                 values: Dict[str, FbsEnumValue],
                 values_by_id: List[FbsEnumValue],
                 is_union: bool,
                 underlying_type: int,
                 attrs: Dict[str, FbsAttribute],
                 docs: str):
        self._repository = repository
        self._schema = schema
        self._declaration_file = declaration_file
        self._name = name
        self._id = id
        self._values = values
        self._values_by_id = values_by_id
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
    def declaration_file(self):
        return self._declaration_file

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def values(self):
        return self._values

    @property
    def values_by_id(self):
        return self._values_by_id

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
            'id': self._id,
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
                 fbs_files: List[Dict[str, str]],
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
        :param fbs_files:
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
        self._fbs_files = fbs_files
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
    def fbs_files(self):
        return self._fbs_files

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
                'files': self._fbs_files,
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
    def load(repository: 'FbsRepository',
             sfile: Union[str, io.RawIOBase, IO[bytes]],
             filename: Optional[str] = None) -> 'FbsSchema':
        """

        :param repository:
        :param sfile:
        :param filename:
        :return:
        """
        data: bytes
        if type(sfile) == str and os.path.isfile(sfile):
            with open(sfile, 'rb') as fd:
                data = fd.read()
        else:
            data = sfile.read()
        m = hashlib.sha256()
        m.update(data)
        # print('loading schema file "{}" ({} bytes, SHA256 0x{})'.format(filename, len(data), m.hexdigest()))

        # get root object in Flatbuffers reflection schema
        # see: https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs
        root = _Schema.GetRootAsSchema(data, 0)

        file_ident = root.FileIdent()
        if file_ident is not None:
            file_ident = file_ident.decode('utf8')

        file_ext = root.FileExt()
        if file_ext is not None:
            file_ext = file_ext.decode('utf8')

        fbs_files = []
        for i in range(root.FbsFilesLength()):
            # zlmdb.flatbuffers.reflection.SchemaFile.SchemaFile
            schema_file = root.FbsFiles(i)
            schema_file_filename = schema_file.Filename()
            if schema_file_filename:
                schema_file_filename = schema_file_filename.decode('utf8')
            schema_file_included_filenames = []
            for j in range(schema_file.IncludedFilenamesLength()):
                included_filename = schema_file.IncludedFilenames(j)
                if included_filename:
                    included_filename = included_filename.decode('utf8')
                schema_file_included_filenames.append(included_filename)
            fbs_files.append(
                {
                    'filename': schema_file_filename,
                    'included_filenames': schema_file_included_filenames,
                }
            )

        root_table = root.RootTable()
        if root_table is not None:
            root_table = FbsObject.parse(repository, root_table)

        schema = FbsSchema(repository=repository,
                           file_name=filename,
                           file_size=len(data),
                           file_sha256=m.hexdigest(),
                           file_ident=file_ident,
                           file_ext=file_ext,
                           fbs_files=fbs_files,
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

            enum_declaration_file = fbs_enum.DeclarationFile()
            if enum_declaration_file:
                enum_declaration_file = enum_declaration_file.decode('utf8')

            enum_underlying_type = fbs_enum.UnderlyingType()

            enum_values = {}
            enum_values_by_id = []
            for j in range(fbs_enum.ValuesLength()):
                fbs_enum_value = fbs_enum.Values(j)
                enum_value_name = fbs_enum_value.Name()
                if enum_value_name:
                    enum_value_name = enum_value_name.decode('utf8')
                enum_value_value = fbs_enum_value.Value()
                enum_value_docs = parse_docs(fbs_enum_value)
                enum_value = FbsEnumValue(repository=repository,
                                          schema=schema,
                                          name=enum_value_name,
                                          id=j,
                                          value=enum_value_value,
                                          docs=enum_value_docs)
                assert enum_value_name not in enum_values
                enum_values[enum_value_name] = enum_value
                enum_values_by_id.append(enum_value)

            enum = FbsEnum(repository=repository,
                           schema=schema,
                           declaration_file=enum_declaration_file,
                           name=enum_name,
                           id=i,
                           values=enum_values,
                           values_by_id=enum_values_by_id,
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
            # print('ok, processed schema object "{}"'.format(obj.name))
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

            svc_declaration_file = svc_obj.DeclarationFile()
            if svc_declaration_file:
                svc_declaration_file = svc_declaration_file.decode('utf8')

            docs = parse_docs(svc_obj)
            attrs = parse_attr(svc_obj)
            calls, calls_by_id = parse_calls(repository, schema, svc_obj, objs_lst=objs_by_id)

            service = FbsService(repository=repository,
                                 schema=schema,
                                 declaration_file=svc_declaration_file,
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


def validate_scalar(field, value: Optional[Any]):
    # print('validate scalar "{}" for type {} (attrs={})'.format(field.name,
    #                                                            FbsType.FBS2STR[field.type.basetype],
    #                                                            field.attrs))
    if field.type.basetype in FbsType.FBS2PY_TYPE:
        expected_type = FbsType.FBS2PY_TYPE[field.type.basetype]
        if type(value) != expected_type:
            raise InvalidPayload('invalid type {} for value, expected {}'.format(type(value), expected_type))
    else:
        assert False, 'FIXME'


class FbsRepository(object):
    """
    crossbar.interfaces.IInventory
      - add: FbsRepository[]
        - load: FbsSchema[]

    https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs
    """

    def __init__(self, basemodule: str):
        self.log = txaio.make_logger()
        self._basemodule = basemodule
        self._schemata: Dict[str, FbsSchema] = {}
        self._objs: Dict[str, FbsObject] = {}
        self._enums: Dict[str, FbsEnum] = {}
        self._services: Dict[str, FbsService] = {}

    @staticmethod
    def from_archive(filename: str) -> 'FbsRepository':
        catalog = FbsRepository()
        return catalog

    @staticmethod
    def from_address(address: str) -> 'FbsRepository':
        catalog = FbsRepository()
        return catalog

    @property
    def basemodule(self) -> str:
        return self._basemodule

    @property
    def schemas(self) -> Dict[str, FbsSchema]:
        return self._schemata

    @property
    def objs(self) -> Dict[str, FbsObject]:
        return self._objs

    @property
    def enums(self) -> Dict[str, FbsEnum]:
        return self._enums

    @property
    def services(self) -> Dict[str, FbsService]:
        return self._services

    @property
    def total_count(self):
        return len(self._objs) + len(self._enums) + len(self._services)

    def load(self, filename: str) -> Tuple[int, int]:
        """
        Load and add all schemata from Flatbuffers binary schema files (`*.bfbs`)
        found in the given directory. Alternatively, a path to a single schema file
        can be provided.

        :param filename: Filesystem path of a directory or single file from which to
            load and add Flatbuffers schemata.
        """
        file_dups = 0
        load_from_filenames = []
        if os.path.isdir(filename):
            for path in Path(filename).rglob('*.bfbs'):
                fn = os.path.join(filename, path.name)
                if fn not in self._schemata:
                    load_from_filenames.append(fn)
                else:
                    # print('duplicate schema file skipped ("{}" already loaded)'.format(fn))
                    file_dups += 1
        elif os.path.isfile(filename):
            if filename not in self._schemata:
                load_from_filenames.append(filename)
            else:
                # print('duplicate schema file skipped ("{}" already loaded)'.format(filename))
                file_dups += 1
        elif ',' in filename:
            for filename_single in filename.split(','):
                filename_single = os.path.expanduser(filename_single)
                # filename_single = os.path.expandvars(filename_single)
                if os.path.isfile(filename_single):
                    if filename_single not in self._schemata:
                        load_from_filenames.append(filename_single)
                    else:
                        print('duplicate schema file skipped ("{}" already loaded)'.format(filename_single))
                else:
                    raise RuntimeError('"{}" in list is not a file'.format(filename_single))
        else:
            raise RuntimeError('cannot open schema file or directory: "{}"'.format(filename))

        enum_dups = 0
        obj_dups = 0
        svc_dups = 0

        # iterate over all schema files found
        for fn in load_from_filenames:
            # load this schema file
            schema: FbsSchema = FbsSchema.load(self, fn)

            # add enum types to repository by name
            for enum in schema.enums.values():
                if enum.name in self._enums:
                    # print('skipping duplicate enum type for name "{}"'.format(enum.name))
                    enum_dups += 1
                else:
                    self._enums[enum.name] = enum

            # add object types
            for obj in schema.objs.values():
                if obj.name in self._objs:
                    # print('skipping duplicate object (table/struct) type for name "{}"'.format(obj.name))
                    obj_dups += 1
                else:
                    self._objs[obj.name] = obj

            # add service definitions ("APIs")
            for svc in schema.services.values():
                if svc.name in self._services:
                    # print('skipping duplicate service type for name "{}"'.format(svc.name))
                    svc_dups += 1
                else:
                    self._services[svc.name] = svc

            self._schemata[fn] = schema

        type_dups = enum_dups + obj_dups + svc_dups
        return file_dups, type_dups

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

    def print_summary(self):
        # brown = (160, 110, 50)
        # brown = (133, 51, 51)
        brown = (51, 133, 255)
        # steel_blue = (70, 130, 180)
        orange = (255, 127, 36)
        # deep_pink = (255, 20, 147)
        # light_pink = (255, 102, 204)
        # pink = (204, 82, 163)
        pink = (127, 127, 127)

        for obj_key, obj in self.objs.items():
            prefix_uri = obj.attrs.get('wampuri', self._basemodule)
            obj_name = obj_key.split('.')[-1]
            obj_color = 'blue' if obj.is_struct else brown
            obj_label = '{} {}'.format('Struct' if obj.is_struct else 'Table', obj_name)
            print('{}\n'.format(hlval('   {} {} {}'.format('====', obj_label, '=' * (118 - len(obj_label))),
                                      color=obj_color)))
            # print('   {} {} {}\n'.format(obj_kind, hlval(obj_name, color=obj_color), '=' * (120 - len(obj_name))))

            if prefix_uri:
                print('    Type URI:  {}.{}'.format(hlval(prefix_uri), hlval(obj_name)))
            else:
                print('    Type URI:  {}'.format(hlval(obj_name)))
            print()
            print(textwrap.fill(obj.docs,
                                width=100,
                                initial_indent='    ',
                                subsequent_indent='    ',
                                expand_tabs=True,
                                replace_whitespace=True,
                                fix_sentence_endings=False,
                                break_long_words=True,
                                drop_whitespace=True,
                                break_on_hyphens=True,
                                tabsize=4))
            print()
            for field in obj.fields_by_id:
                docs = textwrap.wrap(field.docs,
                                     width=70,
                                     initial_indent='',
                                     subsequent_indent='',
                                     expand_tabs=True,
                                     replace_whitespace=True,
                                     fix_sentence_endings=False,
                                     break_long_words=True,
                                     drop_whitespace=True,
                                     break_on_hyphens=True,
                                     tabsize=4)
                if field.type.basetype == FbsType.Obj:
                    type_desc_str = field.type.objtype.split('.')[-1]
                    if self.objs[field.type.objtype].is_struct:
                        type_desc = hlval(type_desc_str, color='blue')
                    else:
                        type_desc = hlval(type_desc_str, color=brown)
                elif field.type.basetype == FbsType.Vector:
                    type_desc_str = 'Vector[{}]'.format(FbsType.FBS2STR[field.type.element])
                    type_desc = hlval(type_desc_str, color='white')
                else:
                    type_desc_str = FbsType.FBS2STR[field.type.basetype]
                    type_desc = hlval(type_desc_str, color='white')

                if field.attrs:
                    attrs_text_str = '(' + ', '.join(field.attrs.keys()) + ')'
                    attrs_text = hlval(attrs_text_str, color=pink)
                    type_text_str = ' '.join([type_desc_str, attrs_text_str])
                    type_text = ' '.join([type_desc, attrs_text])
                else:
                    type_text_str = type_desc_str
                    type_text = type_desc

                # print('>>', len(type_text_str), len(type_text))

                print('    {:<36} {} {}'.format(hlval(field.name),
                                                type_text + ' ' * (28 - len(type_text_str)),
                                                docs[0] if docs else ''))
                for line in docs[1:]:
                    print(' ' * 57 + line)
            print()

        for svc_key, svc in self.services.items():
            prefix_uri = svc.attrs.get('wampuri', self._basemodule)
            ifx_uuid = svc.attrs.get('uuid', None)
            ifc_name = svc_key.split('.')[-1]
            ifc_label = 'Interface {}'.format(ifc_name)
            print('{}\n'.format(hlval('   {} {} {}'.format('====', ifc_label, '=' * (118 - len(ifc_label))),
                                      color='yellow')))
            print('    Interface UUID:  {}'.format(hlval(ifx_uuid)))
            print('    Interface URIs:  {}.({}|{})'.format(hlval(prefix_uri), hlval('procedure', color=orange),
                                                           hlval('topic', color='green')))
            print()
            print(textwrap.fill(svc.docs,
                                width=100,
                                initial_indent='    ',
                                subsequent_indent='    ',
                                expand_tabs=True,
                                replace_whitespace=True,
                                fix_sentence_endings=False,
                                break_long_words=True,
                                drop_whitespace=True,
                                break_on_hyphens=True,
                                tabsize=4))
            for uri in svc.calls.keys():
                print()
                ep: FbsRPCCall = svc.calls[uri]
                ep_type = ep.attrs['type']
                ep_color = {'topic': 'green', 'procedure': orange}.get(ep_type, 'white')
                # uri_long = '{}.{}'.format(hlval(prefix_uri, color=(127, 127, 127)),
                #                           hlval(ep.attrs.get('wampuri', ep.name), color='white'))
                uri_short = '{}'.format(hlval(ep.attrs.get('wampuri', ep.name), color=(255, 255, 255)))
                print('      {} {} ({}) -> {}'.format(hlval(ep_type, color=ep_color),
                                                      uri_short,
                                                      hlval(ep.request.name.split('.')[-1], color='blue', bold=False),
                                                      hlval(ep.response.name.split('.')[-1], color='blue', bold=False)))
                print()
                print(textwrap.fill(ep.docs,
                                    width=90,
                                    initial_indent='          ',
                                    subsequent_indent='          ',
                                    expand_tabs=True,
                                    replace_whitespace=True,
                                    fix_sentence_endings=False,
                                    break_long_words=True,
                                    drop_whitespace=True,
                                    break_on_hyphens=True,
                                    tabsize=4))
            print()

    def render(self, jinja2_env, output_dir, output_lang):
        """

        :param jinja2_env:
        :param output_dir:
        :param output_lang:
        :return:
        """
        # type categories in schemata in the repository
        #
        work = {
            'obj': self.objs.values(),
            'enum': self.enums.values(),
            'service': self.services.values(),
        }

        # collect code sections by module
        #
        code_modules = {}
        test_code_modules = {}
        is_first_by_category_modules = {}

        for category, values in work.items():
            # generate and collect code for all FlatBuffers items in the given category
            # and defined in schemata previously loaded int

            for item in values:
                # metadata = item.marshal()
                # pprint(item.marshal())
                metadata = item

                # com.example.device.HomeDeviceVendor => com.example.device
                modulename = '.'.join(metadata.name.split('.')[0:-1])
                metadata.modulename = modulename

                # com.example.device.HomeDeviceVendor => HomeDeviceVendor
                metadata.classname = metadata.name.split('.')[-1].strip()

                # com.example.device => device
                metadata.module_relimport = modulename.split('.')[-1]

                is_first = modulename not in code_modules
                is_first_by_category = (modulename, category) not in is_first_by_category_modules

                if is_first_by_category:
                    is_first_by_category_modules[(modulename, category)] = True

                # render template into python code section
                if output_lang == 'python':
                    # render obj|enum|service.py.jinja2 template
                    tmpl = jinja2_env.get_template('py-autobahn/{}.py.jinja2'.format(category))
                    code = tmpl.render(repo=self, metadata=metadata, FbsType=FbsType,
                                       render_imports=is_first,
                                       is_first_by_category=is_first_by_category,
                                       render_to_basemodule=self.basemodule)

                    # FIXME
                    # code = FormatCode(code)[0]

                    # render test_obj|enum|service.py.jinja2 template
                    test_tmpl = jinja2_env.get_template('py-autobahn/test_{}.py.jinja2'.format(category))
                    test_code = test_tmpl.render(repo=self, metadata=metadata, FbsType=FbsType,
                                                 render_imports=is_first,
                                                 is_first_by_category=is_first_by_category,
                                                 render_to_basemodule=self.basemodule)

                elif output_lang == 'eip712':
                    # render obj|enum|service-eip712.sol.jinja2 template
                    tmpl = jinja2_env.get_template('so-eip712/{}-eip712.sol.jinja2'.format(category))
                    code = tmpl.render(repo=self, metadata=metadata, FbsType=FbsType,
                                       render_imports=is_first,
                                       is_first_by_category=is_first_by_category,
                                       render_to_basemodule=self.basemodule)

                    # FIXME
                    # code = FormatCode(code)[0]

                    test_tmpl = None
                    test_code = None

                elif output_lang == 'json':
                    code = json.dumps(metadata.marshal(),
                                      separators=(', ', ': '),
                                      ensure_ascii=False,
                                      indent=4,
                                      sort_keys=True)
                    test_code = None
                else:
                    raise RuntimeError('invalid language "{}" for code generation'.format(output_lang))

                # collect code sections per-module
                if modulename not in code_modules:
                    code_modules[modulename] = []
                    test_code_modules[modulename] = []
                code_modules[modulename].append(code)
                if test_code:
                    test_code_modules[modulename].append(test_code)
                else:
                    test_code_modules[modulename].append(None)

        # ['', 'com.example.bla.blub', 'com.example.doo']
        namespaces = {}
        for code_file in code_modules.keys():
            name_parts = code_file.split('.')
            for i in range(len(name_parts)):
                pn = name_parts[i]
                ns = '.'.join(name_parts[:i])
                if ns not in namespaces:
                    namespaces[ns] = []
                if pn and pn not in namespaces[ns]:
                    namespaces[ns].append(pn)

        print('Namespaces:\n{}\n'.format(pformat(namespaces)))

        # write out code modules
        #
        i = 0
        initialized = set()
        for code_file, code_sections in code_modules.items():
            code = '\n\n\n'.join(code_sections)
            if code_file:
                code_file_dir = [''] + code_file.split('.')[0:-1]
            else:
                code_file_dir = ['']

            # FIXME: cleanup this mess
            for i in range(len(code_file_dir)):
                d = os.path.join(output_dir, *(code_file_dir[:i + 1]))
                if not os.path.isdir(d):
                    os.mkdir(d)
                if output_lang == 'python':
                    fn = os.path.join(d, '__init__.py')

                    _modulename = '.'.join(code_file_dir[:i + 1])[1:]
                    _imports = namespaces[_modulename]
                    tmpl = jinja2_env.get_template('py-autobahn/module.py.jinja2')
                    init_code = tmpl.render(repo=self, modulename=_modulename, imports=_imports,
                                            render_to_basemodule=self.basemodule)
                    data = init_code.encode('utf8')

                    if not os.path.exists(fn):
                        with open(fn, 'wb') as f:
                            f.write(data)
                        print('Ok, rendered "module.py.jinja2" in {} bytes to "{}"'.format(len(data), fn))
                        initialized.add(fn)
                    else:
                        with open(fn, 'ab') as f:
                            f.write(data)

            if output_lang == 'python':
                if code_file:
                    code_file_name = '{}.py'.format(code_file.split('.')[-1])
                    test_code_file_name = 'test_{}.py'.format(code_file.split('.')[-1])
                else:
                    code_file_name = '__init__.py'
                    test_code_file_name = None
            elif output_lang == 'json':
                if code_file:
                    code_file_name = '{}.json'.format(code_file.split('.')[-1])
                else:
                    code_file_name = 'init.json'
                test_code_file_name = None
            else:
                code_file_name = None
                test_code_file_name = None

            # write out code modules
            #
            if code_file_name:
                try:
                    code = FormatCode(code)[0]
                except Exception as e:
                    print('error during formatting code: {}'.format(e))
                data = code.encode('utf8')

                fn = os.path.join(*(code_file_dir + [code_file_name]))
                fn = os.path.join(output_dir, fn)

                # FIXME
                # if fn not in initialized and os.path.exists(fn):
                #     os.remove(fn)
                #     with open(fn, 'wb') as fd:
                #         fd.write('# Generated by Autobahn v{}\n'.format(__version__).encode('utf8'))
                #     initialized.add(fn)

                with open(fn, 'ab') as fd:
                    fd.write(data)

                print('Ok, written {} bytes to {}'.format(len(data), fn))

            # write out unit test code modules
            #
            if test_code_file_name:
                test_code_sections = test_code_modules[code_file]
                test_code = '\n\n\n'.join(test_code_sections)
                try:
                    test_code = FormatCode(test_code)[0]
                except Exception as e:
                    print('error during formatting code: {}'.format(e))
                data = test_code.encode('utf8')

                fn = os.path.join(*(code_file_dir + [test_code_file_name]))
                fn = os.path.join(output_dir, fn)

                if fn not in initialized and os.path.exists(fn):
                    os.remove(fn)
                    with open(fn, 'wb') as fd:
                        fd.write('# Copyright (c) ...\n'.encode('utf8'))
                    initialized.add(fn)

                with open(fn, 'ab') as fd:
                    fd.write(data)

                print('Ok, written {} bytes to {}'.format(len(data), fn))

    def validate_obj(self, validation_type: Optional[str], value: Optional[Any]):
        """
        Validate value against the validation type given.

        If the application payload does not validate against the provided type,
        an :class:`autobahn.wamp.exception.InvalidPayload` is raised.

        :param validation_type: Flatbuffers type (fully qualified) against to validate application payload.
        :param value: Value to validate.
        :return:
        """
        # print('validate_obj', validation_type, type(value))

        if validation_type is None:
            # any value validates against the None validation type
            return

        if validation_type not in self.objs:
            raise RuntimeError('validation type "{}" not found in inventory'.format(self.objs))

        # the Flatbuffers table type from the realm's type inventory against which we
        # will validate the WAMP args/kwargs application payload
        vt: FbsObject = self.objs[validation_type]

        if type(value) == dict:
            vt_kwargs = set(vt.fields.keys())

            for k, v in value.items():
                if k not in vt.fields:
                    raise InvalidPayload('unexpected argument "{}" in value of validation type "{}"'.format(k, vt.name))
                vt_kwargs.discard(k)

                field = vt.fields[k]

                # validate object-typed field, eg "uint160_t"
                if field.type.basetype == FbsType.Obj:
                    self.validate_obj(field.type.objtype, v)

                elif field.type.basetype == FbsType.Union:
                    pass
                    print('FIXME-003-Union')

                elif field.type.basetype == FbsType.Vector:
                    if isinstance(v, str) or isinstance(v, bytes):
                        print('FIXME-003-1-Vector')
                    elif isinstance(v, Sequence):
                        for ve in v:
                            self.validate_obj(field.type.elementtype, ve)
                    else:
                        raise InvalidPayload('invalid type {} for value (expected Vector/List/Tuple) '
                                             'of validation type "{}"'.format(type(v), vt.name))

                else:
                    validate_scalar(field, v)

            if vt.is_struct and vt_kwargs:
                raise InvalidPayload('missing argument(s) {} in validation type "{}"'.format(list(vt_kwargs), vt.name))

        elif type(value) in [tuple, list]:
            # FIXME: KeyValues
            if not vt.is_struct:
                raise InvalidPayload('**: invalid type {} for (non-struct) validation type "{}"'.format(type(value), vt.name))

            idx = 0
            for field in vt.fields_by_id:
                # consume the next positional argument from input
                if idx >= len(value):
                    raise InvalidPayload('missing argument "{}" in type "{}"'.format(field.name, vt.name))
                v = value[idx]
                idx += 1

                # validate object-typed field, eg "uint160_t"
                if field.type.basetype == FbsType.Obj:
                    self.validate_obj(field.type.objtype, v)

                elif field.type.basetype == FbsType.Union:
                    pass
                    print('FIXME-005-Union')

                elif field.type.basetype == FbsType.Vector:
                    if isinstance(v, str) or isinstance(v, bytes):
                        print('FIXME-005-1-Vector')
                    elif isinstance(v, Sequence):
                        for ve in v:
                            print(field.type.elementtype, ve)
                            self.validate_obj(field.type.elementtype, ve)
                    else:
                        print('FIXME-005-3-Vector')

                else:
                    validate_scalar(field, v)

            if len(value) > idx:
                raise InvalidPayload('unexpected argument(s) in validation type "{}"'.format(vt.name))

        else:
            raise InvalidPayload('invalid type {} for value of validation type "{}"'.format(type(value), vt.name))

    def validate(self, validation_type: str, args: List[Any], kwargs: Dict[str, Any]) -> Optional[FbsObject]:
        """
        Validate the WAMP application payload provided in positional argument in ``args``
        and in keyword-based arguments in ``kwargs`` against the FlatBuffers table
        type ``validation_type`` from this repository.

        If the application payload does not validate against the provided type,
        an :class:`autobahn.wamp.exception.InvalidPayload` is raised.

        :param validation_type: Flatbuffers type (fully qualified) against to validate application payload.
        :param args: The application payload WAMP positional arguments.
        :param kwargs: The application payload WAMP keyword-based arguments.
        :return: The validation type object from this repository (reference in ``validation_type``)
            which has been used for validation.
        """
        # any value validates against the None validation type
        if validation_type is None:
            return None

        if validation_type not in self.objs:
            raise RuntimeError('validation type "{}" not found in inventory (among {} types)'.format(validation_type, len(self.objs)))

        # the Flatbuffers table type from the realm's type inventory against which we
        # will validate the WAMP args/kwargs application payload
        vt: FbsObject = self.objs[validation_type]

        # we use this to index and consume positional args from the input
        args_idx = 0

        # we use this to track any kwargs not consumed while processing the validation type.
        # and names left in this set after processing the validation type in full is an error ("unexpected kwargs")
        kwargs_keys = set(kwargs.keys() if kwargs else [])

        # iterate over all fields of validation type in field index order (!)
        for field in vt.fields_by_id:

            # field is a WAMP positional argument, that is one that needs to map to the next arg from args
            if field.required or 'arg' in field.attrs or 'kwarg' not in field.attrs:
                # consume the next positional argument from input
                if args is None or args_idx >= len(args):
                    raise InvalidPayload('missing positional argument "{}" in type "{}"'.format(field.name, vt.name))
                value = args[args_idx]
                args_idx += 1

                # validate object-typed field, eg "uint160_t"
                if field.type.basetype == FbsType.Obj:
                    self.validate_obj(field.type.objtype, value)

                elif field.type.basetype == FbsType.Union:
                    pass
                    print('FIXME-003-Union')

                elif field.type.basetype == FbsType.Vector:

                    if isinstance(value, str) or isinstance(value, bytes):
                        print('FIXME-005-1-Vector')
                    elif isinstance(value, Sequence):
                        for ve in value:
                            print(field.type.elementtype, ve)
                            self.validate_obj(field.type.elementtype, ve)
                    else:
                        print('FIXME-005-3-Vector')

                else:
                    validate_scalar(field, value)

            # field is a WAMP keyword argument, that is one that needs to map into kwargs
            elif 'kwarg' in field.attrs:
                if field.name in kwargs_keys:
                    value = kwargs[field.name]
                    # FIXME: validate value vs field type
                    print('FIXME-003')
                    kwargs_keys.discard(field.name)
            else:
                assert False, 'should not arrive here'

        if len(args) > args_idx:
            raise InvalidPayload('{} unexpected positional arguments in type "{}"'.format(len(args) - args_idx, vt.name))

        if kwargs_keys:
            raise InvalidPayload('{} unexpected keyword arguments {} in type "{}"'.format(len(kwargs_keys), list(kwargs_keys), vt.name))

        return vt
