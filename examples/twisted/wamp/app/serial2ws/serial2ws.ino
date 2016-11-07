///////////////////////////////////////////////////////////////////////////////
//
// The MIT License (MIT)
// 
// Copyright (c) Crossbar.io Technologies GmbH
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
///////////////////////////////////////////////////////////////////////////////

const int ledPin = 3;
const int pot1Pin = 0;
const int pot2Pin = 1;

const int minVal = 0;
const int maxVal = 400;

int last1 = 0;
int last2 = 0;

HardwareSerial *port;


void setup() {

// We need to use different serial ports on different Arduinos
//
// See:
//   - Arduino/hardware/tools/avr/avr/include/avr/io.h
//   - http://electronics4dogs.blogspot.de/2011/01/arduino-predefined-constants.html
//
#ifdef __AVR_ATmega32U4__
   port = &Serial1; // Arduino Yun
#else
   port = &Serial;  // Arduino Mega and others
#endif

   port->begin(9600);

   pinMode(ledPin, OUTPUT);
   digitalWrite(ledPin, LOW);
}


void getAnalog(int pin, int id, int *last) {
   // read analog value and map/constrain to output range
   int cur = constrain(map(analogRead(pin), 0, 1023, minVal, maxVal), minVal, maxVal);
  
   // if value changed, forward on serial (as ASCII)
   if (cur != *last) {
      *last = cur;
      port->print(id);
      port->print('\t');
      port->print(*last);
      port->println();
   }  
}


void loop() {
  
   // control LED via commands read from serial  
   if (port->available()) {
      int inByte = port->read();
      if (inByte == '0') {
         digitalWrite(ledPin, LOW);
      } else if (inByte == '1') {
         digitalWrite(ledPin, HIGH);
      }
   }
  
   getAnalog(pot1Pin, 0, &last1);
   getAnalog(pot2Pin, 1, &last2);

   // limit update frequency to 50Hz
   delay(20);
}
