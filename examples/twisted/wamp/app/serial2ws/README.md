# Bridging an Arduino to WebSocket/WAMP

This demo shows how to hook up an Arduino to a WAMP router and display real-time sensor readings in a browser, as well as control the Arduino from the browser.

To give you an idea, here are some videos:

* [Arduino Yun + Browser](https://www.youtube.com/watch?v=Egvu4jL_Wlo)
* [Arduino Mega + Browser](https://www.youtube.com/watch?v=va7j86thW5M)


## How it works

The `serial2ws` program will open a serial port connection with your Arduino. It will communicate over a simple, ASCII based protocol with your device.

### Control

The `serial2ws` program exposes a WAMP procedure `com.myapp.mcu.control_led` which can be called remotely via WAMP. When the procedure is called, `serial2py` forwards the control command to the Arduino over serial. Turning on and off the LED is done by sending a `0` or `1` character over serial.

### Sense

The Arduino will send sensor analog values by sending ASCII lines over serial consisting of the sensor ID (int) and sensor value (int) delimited by whitespace (a tab character). The `serial2ws` will receive those lines, parse each line, and then publish WAMP events with the payload consisting of the sensor values to the topic `com.myapp.mcu.on_analog_value`.


## How to run

You will need to have the following installed onn the host that connects over serial to your Arduino. 

* Python
* Twisted
* AutobahnPython
* PySerial

> When using the Arduino Yun, this stuff runs on the little Linux computer that resides on the Yun. When using the Arduino Mega, this stuff runs on a computer to which you connect the Mega via serial.

Upload the `serial2ws.ino` sketch to your Arduino.

Connect your serial device and run

    python serial2ws.py

Open

    http://localhost:8000/

in your browser.

> The `serial2ws` program has a number of command line options for setting COM port, baudrate etc.
> Run `python serial2ws.py --help` to get information on those.


**Examples**

Arduino Yun running an embedded Web server and WAMP router:

	python serial2ws.py --port /dev/ttyATH0

Arduino Yun running disabling the embedded Web server and connecting to an uplink WAMP router:

	python serial2ws.py --port /dev/ttyATH0 --web 0 --router ws://192.168.1.130:8080/ws
