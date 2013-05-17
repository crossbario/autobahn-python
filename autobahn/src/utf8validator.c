/*
 * utf8validator.c
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

#define UTF8_ACCEPT 0
#define UTF8_REJECT 1

static const char UTF8VALIDATOR_DFA[] = {
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 00..1f
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 20..3f
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 40..5f
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 60..7f
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9, // 80..9f
    7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7, // a0..bf
    8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, // c0..df
    0xa,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x4,0x3,0x3, // e0..ef
    0xb,0x6,0x6,0x6,0x5,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8, // f0..ff
    0x0,0x1,0x2,0x3,0x5,0x8,0x7,0x1,0x1,0x1,0x4,0x6,0x1,0x1,0x1,0x1, // s0..s0
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1, // s1..s2
    1,2,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1, // s3..s4
    1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1, // s5..s6
    1,3,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1  // s7..s8
};

// Utf8Validator type struct
typedef struct
{
    PyObject_HEAD
    int i;
    int state;
} Utf8Validator;

static PyMemberDef Utf8Validator_members[] =
{
    {"i", T_INT, offsetof(Utf8Validator, i), 0, "Total index of validator."},
    {"state", T_INT, offsetof(Utf8Validator, state), 0, "State of validator."},
    {NULL}
};

// Common method
static void reset(Utf8Validator *self)
{
    self->i = 0;
    self->state = UTF8_ACCEPT;
}

// Utf8Validator - tp_init
static int Utf8Validator_tp_init(Utf8Validator *self, PyObject *args, PyObject *kwargs)
{
    /* Check if there are no arguments given */
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "Utf8Validator.__init__() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return -1;
    }
    
    /* Initialize the validator */
    reset(self);
    
    return 0;
}

// Utf8Validator - tp_dealloc
static void Utf8Validator_tp_dealloc(Utf8Validator *self)
{
    self->ob_type->tp_free((PyObject*)self);
}

// Utf8Validator - reset
static PyObject* Utf8Validator_reset(Utf8Validator *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "Utf8Validator.reset() takes no parameters (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }
    
    /* Reset the validator */
    reset(self);
    
    Py_RETURN_NONE;
}

// Utf8Validator - validate
static PyObject* Utf8Validator_validate(Utf8Validator *self, PyObject *args)
{
    /* Declarations */
    int valid;
    int state;
    int i;
    uint8_t *buf;
    Py_ssize_t buf_len;
    PyObject *py_buf;
    
    /* Parse input arguments */
    if (!PyArg_ParseTuple(args, "O:validate", &py_buf))
        return NULL;
    
    if (PyObject_AsReadBuffer(py_buf, (const void**) &buf, &buf_len))
        return NULL;
    
    /* Initialize local variables */
    valid = 1;
    state = self->state;
    
    /* Validate bytes */
    for (i = 0; i < (int) buf_len; ++i)
    {
        state = UTF8VALIDATOR_DFA[256 + (state << 4) + UTF8VALIDATOR_DFA[buf[i]]];
        
        if (state == UTF8_REJECT)
        {
            valid = 0;
            break;
        }
    }
    
    /* Store results of validation */
    self->i += i;
    self->state = state;
    
    /* Return the results */
    return Py_BuildValue("OOii",
                         valid ? Py_True : Py_False,
                         state == UTF8_ACCEPT ? Py_True : Py_False,
                         i,
                         self->i);
}

static PyMethodDef Utf8Validator_methods[] =
{
    {"reset", (PyCFunction) Utf8Validator_reset, METH_VARARGS,
    "Reset validator to start new incremental UTF-8 decode/validation."},
    {"validate", (PyCFunction) Utf8Validator_validate, METH_VARARGS,
    "Incrementally validate a chunk of bytes provided as bytearray.\n\
\n\
Will return a quad (valid?, endsOnCodePoint?, currentIndex, totalIndex).\n\
\n\
As soon as an octet is encountered which renders the octet sequence\n\
invalid, a quad with valid? == False is returned. currentIndex returns\n\
the index within the currently consumed chunk, and totalIndex the\n\
index within the total consumed sequence that was the point of bail out.\n\
When valid? == True, currentIndex will be len(ba) and totalIndex the\n\
total amount of consumed bytes."},
    {NULL}
};

static PyTypeObject Utf8ValidatorType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.utf8validator.Utf8Validator",             /* tp_name */
    sizeof(Utf8Validator),                              /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) Utf8Validator_tp_dealloc,              /* tp_dealloc */
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
    "Incremental UTF-8 validator with constant memory consumption (minimal state).\n\
\n\
Implements the algorithm \"Flexible and Economical UTF-8 Decoder\" by\n\
Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).", /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    Utf8Validator_methods,                              /* tp_methods */
    Utf8Validator_members,                              /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) Utf8Validator_tp_init,                   /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

// Python 2.7
PyMODINIT_FUNC initutf8validator(void)
{
#ifdef WITH_THREAD /* Python build with threading support? */
    PyEval_InitThreads();
#endif

    /* Declarations */
    PyObject *module;
    
    /* Create the module */
    module = Py_InitModule3("utf8validator", NULL, "utf8validator module");
    
    if (!module)
    {
        // TODO: Add some error message
        return;
    }
    
    /* Fill in missing slots in type Utf8Validator */
    Utf8ValidatorType.tp_new = PyType_GenericNew;
    
    if (PyType_Ready(&Utf8ValidatorType) < 0)
    {
        // TODO: Add some error message
        return;
    }
    
    /* Add the type Utf8Validator to the module */
    Py_INCREF(&Utf8ValidatorType);
    PyModule_AddObject(module, "Utf8Validator", (PyObject*) &Utf8ValidatorType);
}
