# senslify-client
This software acts as companion software for the Senslify sensor visualization tool. 

## Description
Senslify is a sensor data visualization tool written in collaboration between Case Western Reserve University and Cleveland State University. Senslify employs asynchronous programming and enables sensor observation in real-time.

This tool is a client-side tool that employs asyncronous programming to enable capturing sensor data in real-time. Currently, this software is only compatible with TinyOS wireless sensors, however, support for other sensors is a WIP. 

This client software utilizes PySerial and the TinyOS Python support tools to passively listen to connected devices and uploads them to a Senslify compatible server. 

## Requirements
This software employs the Python programming langauge and requires Python version 3.7+. In addition, this software requires the following additional Python software libraries:

+ [aiohttp](https://pypi.org/project/aiohttp/)
+ [pyserial](https://pypi.org/project/pyserial/)
+ [tinyos](https://pypi.org/project/tinyos/)
