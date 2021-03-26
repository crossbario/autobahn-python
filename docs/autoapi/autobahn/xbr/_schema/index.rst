:mod:`autobahn.xbr._schema`
===========================

.. py:module:: autobahn.xbr._schema


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._schema.FbsType
   autobahn.xbr._schema.FbsAttribute
   autobahn.xbr._schema.FbsField
   autobahn.xbr._schema.FbsObject
   autobahn.xbr._schema.FbsRPCCall
   autobahn.xbr._schema.FbsService
   autobahn.xbr._schema.FbsEnumValue
   autobahn.xbr._schema.FbsEnum
   autobahn.xbr._schema.FbsSchema
   autobahn.xbr._schema.FbsRepository



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._schema.parse_attr
   autobahn.xbr._schema.parse_docs
   autobahn.xbr._schema.parse_fields
   autobahn.xbr._schema.parse_calls


.. data:: T_FbsRepository
   

   

.. class:: FbsType(repository: T_FbsRepository, basetype: int, element: int, index: int, objtype: Optional[str] = None)


   Bases: :class:`object`

   Flatbuffers type.

   See: https://github.com/google/flatbuffers/blob/master/reflection/reflection.fbs

   .. attribute:: None_
      

      

   .. attribute:: UType
      

      

   .. attribute:: Bool
      

      

   .. attribute:: Byte
      

      

   .. attribute:: UByte
      

      

   .. attribute:: Short
      

      

   .. attribute:: UShort
      

      

   .. attribute:: Int
      

      

   .. attribute:: UInt
      

      

   .. attribute:: Long
      

      

   .. attribute:: ULong
      

      

   .. attribute:: Float
      

      

   .. attribute:: Double
      

      

   .. attribute:: String
      

      

   .. attribute:: SCALAR_TYPES
      

      

   .. attribute:: Vector
      

      

   .. attribute:: Obj
      

      

   .. attribute:: Union
      

      

   .. attribute:: STRUCTURED_TYPES
      

      

   .. attribute:: FBS2PY
      

      

   .. attribute:: FBS2FLAGS
      

      

   .. attribute:: FBS2PREPEND
      

      

   .. attribute:: FBS2STR
      

      

   .. attribute:: STR2FBS
      

      

   .. method:: basetype(self)
      :property:

      Flatbuffers base type.

      :return:


   .. method:: element(self)
      :property:

      Only if basetype == Vector or basetype == Array.

      :return:


   .. method:: index(self)
      :property:

      If basetype == Object, index into "objects".

      :return:


   .. method:: objtype(self)
      :property:

      If basetype == Object, fully qualified object type name.

      :return:


   .. method:: map(self, language: str, attrs: Optional[Dict] = None, required: Optional[bool] = True) -> str

      :param language:
      :return:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. class:: FbsAttribute


   Bases: :class:`object`

   .. method:: __str__(self)

      Return str(self).



.. class:: FbsField(repository: T_FbsRepository, name: str, type: autobahn.xbr._schema.FbsType, id: int, offset: int, default_int: int, default_real: float, deprecated: bool, required: bool, attrs: Dict[(str, autobahn.xbr._schema.FbsAttribute)], docs: str)


   Bases: :class:`object`

   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: type(self)
      :property:


   .. method:: id(self)
      :property:


   .. method:: offset(self)
      :property:


   .. method:: default_int(self)
      :property:


   .. method:: default_real(self)
      :property:


   .. method:: deprecated(self)
      :property:


   .. method:: required(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. function:: parse_attr(obj)


.. function:: parse_docs(obj)


.. function:: parse_fields(repository, obj, objs_lst=None)


.. function:: parse_calls(repository, svc_obj, objs_lst=None)


.. class:: FbsObject(repository: T_FbsRepository, name: str, fields: Dict[(str, autobahn.xbr._schema.FbsField)], fields_by_id: Dict[(int, str)], is_struct: bool, min_align: int, bytesize: int, attrs: Dict[(str, autobahn.xbr._schema.FbsAttribute)], docs: str)


   Bases: :class:`object`

   .. method:: map(self, language: str) -> str


   .. method:: map_import(self, language: str) -> str


   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: fields(self)
      :property:


   .. method:: fields_by_id(self)
      :property:


   .. method:: is_struct(self)
      :property:


   .. method:: min_align(self)
      :property:


   .. method:: bytesize(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)


   .. method:: parse(repository, fbs_obj, objs_lst=None)
      :staticmethod:



.. class:: FbsRPCCall(repository: T_FbsRepository, name: str, id: int, request: autobahn.xbr._schema.FbsObject, response: autobahn.xbr._schema.FbsObject, docs: str, attrs: Dict[(str, autobahn.xbr._schema.FbsAttribute)])


   Bases: :class:`object`

   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: id(self)
      :property:


   .. method:: request(self)
      :property:


   .. method:: response(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. class:: FbsService(repository: T_FbsRepository, name: str, calls: Dict[(str, autobahn.xbr._schema.FbsRPCCall)], calls_by_id: Dict[(int, str)], attrs: Dict[(str, autobahn.xbr._schema.FbsAttribute)], docs: str)


   Bases: :class:`object`

   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: calls(self)
      :property:


   .. method:: calls_by_id(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. class:: FbsEnumValue(repository, name, value, docs)


   Bases: :class:`object`

   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: value(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. class:: FbsEnum(repository: T_FbsRepository, name: str, values: Dict[(str, autobahn.xbr._schema.FbsEnumValue)], is_union: bool, underlying_type: int, attrs: Dict[(str, autobahn.xbr._schema.FbsAttribute)], docs: str)


   Bases: :class:`object`

   FlatBuffers enum type.

   .. method:: repository(self)
      :property:


   .. method:: name(self)
      :property:


   .. method:: values(self)
      :property:


   .. method:: is_union(self)
      :property:


   .. method:: underlying_type(self)
      :property:


   .. method:: attrs(self)
      :property:


   .. method:: docs(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)



.. class:: FbsSchema(repository: T_FbsRepository, file_name: str, file_sha256: str, file_size: int, file_ident: str, file_ext: str, root_table: autobahn.xbr._schema.FbsObject, root: zlmdb.flatbuffers.reflection.Schema.Schema, objs: Dict[(str, autobahn.xbr._schema.FbsObject)], enums: Dict[(str, autobahn.xbr._schema.FbsEnum)], services: Dict[(str, autobahn.xbr._schema.FbsService)])


   Bases: :class:`object`

   
   .. method:: repository(self)
      :property:


   .. method:: file_name(self)
      :property:


   .. method:: file_sha256(self)
      :property:


   .. method:: file_size(self)
      :property:


   .. method:: file_ident(self)
      :property:


   .. method:: file_ext(self)
      :property:


   .. method:: root_table(self)
      :property:


   .. method:: root(self)
      :property:


   .. method:: objs(self)
      :property:


   .. method:: enums(self)
      :property:


   .. method:: services(self)
      :property:


   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self) -> Dict[(str, object)]

      :return:


   .. method:: load(repository, filename) -> object
      :staticmethod:

      :param filename:
      :return:



.. class:: FbsRepository(render_to_basemodule)


   Bases: :class:`object`

   
   .. method:: summary(self, keys=False)


   .. method:: render_to_basemodule(self)
      :property:


   .. method:: objs(self)
      :property:


   .. method:: enums(self)
      :property:


   .. method:: services(self)
      :property:


   .. method:: load(self, dirname) -> object



