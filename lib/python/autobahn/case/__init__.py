###############################################################################
##
##  Copyright 2011 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

##
## To add new cases
##
##   1) create a class in subdir "case" (derived from Case, and appropriately named)
##   2) import the class here (see below)
##   3) add class to Cases list (see below)
##

##
## Case classes are named "CaseX_Y_Z" where X is from these test case categories:
##
CaseCategories = {"0": "Handshake",
                  "1": "Framing",
                  "2": "Pings/Pongs",
                  "3": "Reserved Bits",
                  "4": "Opcodes",
                  "5": "Fragmentation",
                  "6": "UTF-8 Handling",
                  "7": "Close Handling",
                  "8": "Misc",
                  "9": "Limits/Performance"}

CaseSubCategories = {"1.1": "Text Messages",
                     "1.2": "Binary Messages",
                     "4.1": "Non-control Opcodes",
                     "4.2": "Control Opcodes",
                     "9.1": "Text Message (increasing size)",
                     "9.2": "Binary Message (increasing size)",
                     "9.3": "Fragmented Text Message (fixed size, increasing fragment size)",
                     "9.4": "Fragmented Binary Message (fixed size, increasing fragment size)",
                     "9.5": "Text Message (fixed size, increasing chop size)",
                     "9.6": "Binary Text Message (fixed size, increasing chop size)"}

##
## Cases
##

from case1_1_1 import *
from case1_1_2 import *
from case1_1_3 import *
from case1_1_4 import *
from case1_1_5 import *
from case1_1_6 import *
from case1_1_7 import *
from case1_1_8 import *

from case1_2_1 import *
from case1_2_2 import *
from case1_2_3 import *
from case1_2_4 import *
from case1_2_5 import *
from case1_2_6 import *
from case1_2_7 import *
from case1_2_8 import *

from case2_1 import *
from case2_2 import *
from case2_3 import *
from case2_4 import *
from case2_5 import *
from case2_6 import *
from case2_7 import *
from case2_8 import *
from case2_9 import *
from case2_10 import *
from case2_11 import *

from case3_1 import *
from case3_2 import *
from case3_3 import *
from case3_4 import *
from case3_5 import *
from case3_6 import *
from case3_7 import *

from case4_1_1 import *
from case4_1_2 import *
from case4_1_3 import *
from case4_1_4 import *
from case4_1_5 import *

from case4_2_1 import *
from case4_2_2 import *
from case4_2_3 import *
from case4_2_4 import *
from case4_2_5 import *

from case5_1 import *
from case5_2 import *
from case5_3 import *
from case5_4 import *
from case5_5 import *
from case5_6 import *
from case5_7 import *
from case5_8 import *
from case5_9 import *
from case5_10 import *
from case5_11 import *
from case5_12 import *
from case5_13 import *
from case5_14 import *
from case5_15 import *
from case5_16 import *
from case5_17 import *
from case5_18 import *
from case5_19 import *
from case5_20 import *

from case6_1 import *
from case6_2 import *
from case6_3 import *

from case9_1_1 import *
from case9_1_2 import *
from case9_1_3 import *
from case9_1_4 import *
from case9_1_5 import *
from case9_1_6 import *

from case9_2_1 import *
from case9_2_2 import *
from case9_2_3 import *
from case9_2_4 import *
from case9_2_5 import *
from case9_2_6 import *

from case9_3_1 import *
from case9_3_2 import *
from case9_3_3 import *
from case9_3_4 import *
from case9_3_5 import *
from case9_3_6 import *
from case9_3_7 import *
from case9_3_8 import *
from case9_3_9 import *

from case9_4_1 import *
from case9_4_2 import *
from case9_4_3 import *
from case9_4_4 import *
from case9_4_5 import *
from case9_4_6 import *
from case9_4_7 import *
from case9_4_8 import *
from case9_4_9 import *

from case9_5_1 import *
from case9_5_2 import *
from case9_5_3 import *
from case9_5_4 import *
from case9_5_5 import *
from case9_5_6 import *

from case9_6_1 import *
from case9_6_2 import *
from case9_6_3 import *
from case9_6_4 import *
from case9_6_5 import *
from case9_6_6 import *

##
## This is the list of Case classes that will be run by the fuzzing server/client
##
Cases = []
Cases += [Case1_1_1, Case1_1_2, Case1_1_3, Case1_1_4, Case1_1_5, Case1_1_6, Case1_1_7, Case1_1_8]
Cases += [Case1_2_1, Case1_2_2, Case1_2_3, Case1_2_4, Case1_2_5, Case1_2_6, Case1_2_7, Case1_2_8]
Cases += [Case2_1, Case2_2, Case2_3, Case2_4, Case2_5, Case2_6, Case2_7, Case2_8, Case2_9, Case2_10, Case2_11]
Cases += [Case3_1, Case3_2, Case3_3, Case3_4, Case3_5, Case3_6, Case3_7]
Cases += [Case4_1_1, Case4_1_2, Case4_1_3, Case4_1_4, Case4_1_5]
Cases += [Case4_2_1, Case4_2_2, Case4_2_3, Case4_2_4, Case4_2_5]
Cases += [Case5_1, Case5_2, Case5_3, Case5_4, Case5_5, Case5_6, Case5_7, Case5_8, Case5_9, Case5_10, Case5_11, Case5_12, Case5_13, Case5_14, Case5_15, Case5_16, Case5_17, Case5_18, Case5_19, Case5_20]
Cases += [Case6_1, Case6_2, Case6_3]
Cases += [Case9_1_1, Case9_1_2, Case9_1_3, Case9_1_4, Case9_1_5, Case9_1_6]
Cases += [Case9_2_1, Case9_2_2, Case9_2_3, Case9_2_4, Case9_2_5, Case9_2_6]
Cases += [Case9_3_1, Case9_3_2, Case9_3_3, Case9_3_4, Case9_3_5, Case9_3_6, Case9_3_7, Case9_3_8, Case9_3_9]
Cases += [Case9_4_1, Case9_4_2, Case9_4_3, Case9_4_4, Case9_4_5, Case9_4_6, Case9_4_7, Case9_4_8, Case9_4_9]
Cases += [Case9_5_1, Case9_5_2, Case9_5_3, Case9_5_4, Case9_5_5, Case9_5_6]
Cases += [Case9_6_1, Case9_6_2, Case9_6_3, Case9_6_4, Case9_6_5, Case9_6_6]

## Class1_2_3 => '1.2.3'
##
def caseClasstoId(klass):
   return '.'.join(klass.__name__[4:].split("_"))

## Class1_2_3 => (1, 2, 3)
##
def caseClasstoIdTuple(klass):
   return tuple([int(x) for x in klass.__name__[4:].split("_")])

## '1.2.3' => (1, 2, 3)
##
def caseIdtoIdTuple(id):
   return tuple([int(x) for x in id.split('.')])

## (1, 2, 3) => '1.2.3'
##
def caseIdTupletoId(idt):
   return '.'.join([str(x) for x in list(idt)])


## Index:
## "1.2.3" => Index (1-based) of Case1_2_3 in Cases
##
CasesIndices = {}
i = 1
for c in Cases:
   CasesIndices[caseClasstoId(c)] = i
   i += 1
