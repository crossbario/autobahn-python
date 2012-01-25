###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

// Arduino sketch reading analog values at 5Hz from pins 1,2 and sending
// raw values to serial

void setup() {
   Serial.begin(9600);
}

void loop() {
   Serial.print(analogRead(1));
   Serial.print(" ");
   Serial.print(analogRead(2));
   Serial.println();
   delay(200); // update at 5Hz
}
