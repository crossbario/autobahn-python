Decimal Calculator Service
==========================

This example demonstrates a WAMP component providing a decimal calculator service.

A browser based UI is included which uses AutobahnJS to access
the decimal calculator service.

Further, since it's a standard WAMP service, any WAMP client can use
the service. You could access it i.e. from a native
Android app via AutobahnAndroid or from a remote AutobahnPython based
client.


Running
-------

Run the calculator backend component by doing

    python calculator.py

and open

    http://localhost:8080/

in your browser.


Background
----------

The calculator service performs correct decimal arithmetic, something not available
(out of the box) in JavaScript.


To see this just try

    console.log(1.1 + 2.2);

in your browser. The output is:

    3.3000000000000003

which is not the result a person would expect when using a calculator.


The reason is that JavaScript implements all numbers as IEEE doubles, which is
a binary floating-point type. Since it's a base-2 floating point, certain numbers
cannot be represented exactly. To be precise, any rational number with a divisor
having a prime factor other than 2 cannot be represented exactly. Decimal arithmetic
uses a base-10, which has prime factors 2 and 5, and consequently all rationals which
have no other prime factors in their divisor other than 2 or 5 can be represented exactly.


Anyway, I hope you get what I mean;)

