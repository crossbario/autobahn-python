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

from case1_1_1 import *
from case1_1_2 import *
from case1_1_3 import *
from case1_1_4 import *
from case1_1_5 import *
from case1_1_6 import *
from case1_1_7 import *
from case1_1_8 import *
from case1_1_9 import *
from case1_1_10 import *

from case1_2_1 import *
from case1_2_2 import *
from case1_2_3 import *
from case1_2_4 import *
from case1_2_5 import *
from case1_2_6 import *
from case1_2_7 import *
from case1_2_8 import *
from case1_2_9 import *
from case1_2_10 import *

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

from case5_15 import *
from case5_16 import *


Cases = []
Cases += [Case1_1_1, Case1_1_2, Case1_1_3, Case1_1_4, Case1_1_5, Case1_1_6, Case1_1_7, Case1_1_8, Case1_1_9, Case1_1_10]
Cases += [Case1_2_1, Case1_2_2, Case1_2_3, Case1_2_4, Case1_2_5, Case1_2_6, Case1_2_7, Case1_2_8, Case1_2_9, Case1_2_10]
Cases += [Case2_1, Case2_2, Case2_3, Case2_4, Case2_5, Case2_6, Case2_7, Case2_8, Case2_9, Case2_10, Case2_11]
Cases += [Case3_1, Case3_2, Case3_3, Case3_4, Case3_5, Case3_6, Case3_7]
Cases += [Case4_1_1, Case4_1_2, Case4_1_3, Case4_1_4, Case4_1_5]
Cases += [Case4_2_1, Case4_2_2, Case4_2_3, Case4_2_4, Case4_2_5]
Cases += [Case5_15, Case5_16]

CaseCategories = {"1": "Framing",
                  "2": "Pings/Pongs",
                  "3": "Reserved Bits",
                  "4": "Opcodes",
                  "5": "Fragmentation",
                  "6": "Limits/Performance"}
