/*
 * xormasker.c
 * 
 * Copyright 2013 Dominique Hunziker <dominique.hunziker@gmail.com>
 * Copyright 2013 Dhananjay Sathe <dhananjaysathe@gmail.com>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

#include <Python.h>
#include <structmember.h>

static PyObject *XorMaskerException;

// XorMaskerNull type struct
typedef struct
{
    PyObject_HEAD
    int ptr;
} XorMaskerNull;

// XorMaskerSimple type struct
typedef struct
{
    PyObject_HEAD
    int ptr;
    uint8_t mask[4];
} XorMaskerSimple;

// XorMaskerNull - tp_init
static int XorMaskerNull_tp_init(XorMaskerNull *self, PyObject *args, PyObject *kwargs)
{
    /* Declarations */
    int num_args;
    
    /* Check if there is at most 1 argument given */
    num_args = PyTuple_GET_SIZE(args);
    
    if (kwargs && PyDict_Check(kwargs))
        num_args += PyDict_Size(kwargs);
    
    if (num_args > 1)
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.__init__() takes at most 1 parameter (%d given)",
                     num_args);
        return -1;
    }
    
    /* Initialize the xor masker */
    self->ptr = 0;
    
    return 0;
}

// XorMaskerSimple - tp_init
static int XorMaskerSimple_tp_init(XorMaskerSimple *self, PyObject *args, PyObject *kwargs)
{
    /* Declarations */
    int i;
    char *mask;
    Py_ssize_t mask_size;
    
    /* Extract the argument */
    if (!PyArg_ParseTuple(args, "s#:__init__", &mask, &mask_size))
        return -1;
    
    /* Verify the argument */
    if ((int) mask_size != 4)
    {
        PyErr_SetString(PyExc_TypeError, "Mask has to be of length 4.");
        return -1;
    }
    
    /* Parse the mask */
    for (i = 0; i < 4; ++i)
        self->mask[i] = mask[i];
    
    /* Initialize the xor masker */
    self->ptr = 0;
    
    return 0;
}

// XorMaskerNull - tp_dealloc
static void XorMaskerNull_tp_dealloc(XorMaskerNull *self)
{
    self->ob_type->tp_free((PyObject*)self);
}

// XorMaskerSimple - tp_dealloc
static void XorMaskerSimple_tp_dealloc(XorMaskerSimple *self)
{
    self->ob_type->tp_free((PyObject*)self);
}

// XorMaskerNull - pointer
static PyObject* XorMaskerNull_pointer(XorMaskerNull *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.pointer() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }
    
    return Py_BuildValue("i", self->ptr);
}

// XorMaskerSimple - pointer
static PyObject* XorMaskerSimple_pointer(XorMaskerSimple *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerSimple.pointer() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }
    
    return Py_BuildValue("i", self->ptr);
}

// XorMaskerNull - reset
static PyObject* XorMaskerNull_reset(XorMaskerNull *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.reset() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }
    
    self->ptr = 0;
    
    Py_RETURN_NONE;
}

// XorMaskerSimple - reset
static PyObject* XorMaskerSimple_reset(XorMaskerSimple *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerSimple.reset() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }
    
    self->ptr = 0;
    
    Py_RETURN_NONE;
}

// XorMaskerNull - process
static PyObject* XorMaskerNull_process(XorMaskerNull *self, PyObject *args)
{
    /* Declarations */
    PyObject *data;
    
    /* Extract the argument */
    if (!PyArg_ParseTuple(args, "O:process", &data))
        return NULL;
    
    if (!PyString_Check(data))
    {
        PyErr_SetString(PyExc_TypeError, "data has to be of type string");
        return NULL;
    }
    
    /* Process the data */
    self->ptr += PyString_GET_SIZE(data);
    
    return Py_BuildValue("O", data);
}

// XorMaskerSimple - process
static PyObject* XorMaskerSimple_process(XorMaskerSimple *self, PyObject *args)
{
    /* Declarations */
    int i;
    Py_ssize_t data_size;
    char *data_in;
    char *data_out;
    PyObject *py_data_out;
    
    /* Local references for instance variables */
    int ptr = self->ptr;
    const uint8_t* const mask = self->mask;
    
    /* Extract the argument */
    if (!PyArg_ParseTuple(args, "s#:process", &data_in, &data_size))
        return NULL;
    
    /* Prepare container for return value */
    py_data_out = PyString_FromStringAndSize(NULL, (int) data_size);
    if (!py_data_out)
    {
        PyErr_SetString(XorMaskerException, "Could not allocate output string.");
        return NULL;
    }
    
    data_out = PyString_AsString(py_data_out);
    if (!data_out)
        return NULL;
    
    /* Process the data */
    for (i = 0; i < (int) data_size; ++i)
        data_out[i] = data_in[i] ^ mask[ptr++ & 3]; // == ptr++ % 4
    
    /* Store the updated instance variables */
    self->ptr = ptr;
    
    return py_data_out;
}

static PyMethodDef XorMaskerNull_methods[] =
{
    {"pointer", (PyCFunction) XorMaskerNull_pointer, METH_VARARGS,
    "Get the current count of the mask pointer."},
    {"reset", (PyCFunction) XorMaskerNull_reset, METH_VARARGS,
    "Reset the mask pointer."},
    {"process", (PyCFunction) XorMaskerNull_process, METH_VARARGS,
    "Process the data by applying the bit mask."},
    {NULL}
};

static PyMethodDef XorMaskerSimple_methods[] =
{
    {"pointer", (PyCFunction) XorMaskerSimple_pointer, METH_VARARGS,
    "Get the current count of the mask pointer."},
    {"reset", (PyCFunction) XorMaskerSimple_reset, METH_VARARGS,
    "Reset the mask pointer."},
    {"process", (PyCFunction) XorMaskerSimple_process, METH_VARARGS,
    "Process the data by applying the bit mask."},
    {NULL}
};

static PyTypeObject XorMaskerNullType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.xormasker.XorMaskerNull",                 /* tp_name */
    sizeof(XorMaskerNull),                              /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) XorMaskerNull_tp_dealloc,              /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    0,                                                  /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    0,                                                  /* tp_call */
    0,                                                  /* tp_str */
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags*/
    "XorMasker",                                        /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    XorMaskerNull_methods,                              /* tp_methods */
    0,                                                  /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) XorMaskerNull_tp_init,                   /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

static PyTypeObject XorMaskerSimpleType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.xormasker.XorMaskerSimple",               /* tp_name */
    sizeof(XorMaskerSimple),                            /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) XorMaskerSimple_tp_dealloc,            /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    0,                                                  /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    0,                                                  /* tp_call */
    0,                                                  /* tp_str */
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags*/
    "XorMasker",                                        /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    XorMaskerSimple_methods,                            /* tp_methods */
    0,                                                  /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) XorMaskerSimple_tp_init,                 /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

// module method createXorMasker
static PyObject* createXorMasker(PyObject *module, PyObject *args)
{
    /* Declarations */
    int len;
    PyObject *mask;
    
    /* Extract the arguments */
    if (!PyArg_ParseTuple(args, "O|i", &mask, &len))
        return NULL;
    
    return PyObject_CallFunctionObjArgs((PyObject *) &XorMaskerSimpleType, mask, NULL);
}

static PyMethodDef utf8validator_methods[] =
{
    {"createXorMasker", createXorMasker, METH_VARARGS,
    "Create a new xormasker using provided mask."},
    {NULL}
};

// Python 2.7
PyMODINIT_FUNC initxormasker(void)
{
#ifdef WITH_THREAD /* Python build with threading support? */
    PyEval_InitThreads();
#endif

    /* Declarations */
    PyObject *module;
    
    /* Create the module */
    module = Py_InitModule3("xormasker", utf8validator_methods, "xormasker module");
    
    if (!module)
    {
        // TODO: Add some error message
        return;
    }
    
    /* Register the Exception used in the module */
    XorMaskerException = PyErr_NewException("autobahn.xormasker.XorMaskerException", NULL, NULL);
    
    /* Fill in missing slots in type XorMaskerNullType */
    XorMaskerNullType.tp_new = PyType_GenericNew;
    
    if (PyType_Ready(&XorMaskerNullType) < 0)
    {
        // TODO: Add some error message
        return;
    }
    
    /* Add the type XorMaskerNullType to the module */
    Py_INCREF(&XorMaskerNullType);
    PyModule_AddObject(module, "XorMaskerNull", (PyObject*) &XorMaskerNullType);
    
    /* Fill in missing slots in type XorMaskerSimpleType */
    XorMaskerSimpleType.tp_new = PyType_GenericNew;
    
    if (PyType_Ready(&XorMaskerSimpleType) < 0)
    {
        // TODO: Add some error message
        return;
    }
    
    /* Add the type XorMaskerSimpleType to the module */
    Py_INCREF(&XorMaskerSimpleType);
    PyModule_AddObject(module, "XorMaskerSimple", (PyObject*) &XorMaskerSimpleType);
}
