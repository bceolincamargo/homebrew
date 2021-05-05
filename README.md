# homebrew
homebrew beer webapp
## Features
 
   
# Introduction
Web server created to collect data from a single ESP8256 chip called brewpiless(vitotai)

a single ESP8266 chip to replace RaspberryPI and Arduino.

fermentation temperature controller. The RPI also hosts a web server for the browser-based front-end. 
Using a RPI or a PC allows the maximum power of BrewPi to be used but requires additional hardware (namely a RPI or PC). 

ESP8266 is cheap and powerful WiFi-enabling IOT solution. 
Although it isn't as powerful as a RPI, it's a good solution to maximize the functionality and minimize the cost. Using a single ESP8266 as the temperature controller (replacing Arduino) and as the web server and schedule maintainer (replacing RPI) also reduces the work in building a brewpi system.

This webserver collects temperature data from an webserver running in WIFI chip and saves into a data lake (Hadoop and CentOS 7) running in 2 desktops in my home


## Technologies in use
Hadoop
MongoDB
Python
Flask
HTML
CSS

## infra
![Diagram](/images/diagram.png)

## !!Special Note


## Known issues



## Version History

 * v3.6
    * update framework to 2.2.0
    * **4m2m flash layout for All but SONOFF, due to size growth of framework.**
    * update OLED library to 4.0 (Not verified by me, but SOMEONE@HBT did report working)
    * update to ArduinoJson V6
    * add revised LCD page. at /lcd
    * SOFF OTA configuraton not longer available for space limit
    * Using interrupt for more responsive button operation.
    * MQTT publish/subscribe, NEW UI only.
