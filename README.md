# Senslify Client
This software acts as companion software for the Senslify sensor visualization tool. 


## Description
Senslify is a sensor data visualization tool written in collaboration between Case Western Reserve University and Cleveland State University. Senslify employs asynchronous programming and enables sensor observation in real-time.

This tool is a client-side tool that employs asyncronous programming to enable capturing sensor data in real-time. Currently, this software is only compatible with TinyOS wireless sensors, however, support for other sensors is a WIP. 

The client software utilizes PySerial and the TinyOS Python support tools to passively listen to connected devices and uploads them to a Senslify compatible server. 


## Usage
The client comes bundled with Setuptools support. All you have to install the client is to type `python3 setup.py install` in the projects root directory.

To use the client, you can invoke it from the command line by typing `sdcp`. This will start the client shell.

The first thing you'll want to do upon opening the client is to connect to a Senslify server. If you know the address of the server you want to connect to, type `server set [ADDR]`, where the address is the servers root address without any trailing path. Alternatively, you can specify a default server to connect by customizing the bundled config file.

The list of commands for the client are as follows:
+ cls
+ devices
    + add [DEVICE] [BAUDRATE] [SAMPLERATE]
    + pause [DEVICE]
    + remove [DEVICE]
    + show
    + start [DEVICE]
    + stop [DEVICE]
+ server
    + add [URI]
    + remove [NUM]
    + set [NUM]
    + show
    
    
Commands are grouped into one of two groups: device commands and server commands. 

When sitting at the SDCP shell, you can see the basic commands by typing `help`. To see help on the subcommands available to a group of commands, type `help [command]`.

When adding a device, you are required to input three parameters:
+ device: The physical address of the device.
+ baudrate: The physical sampling rate of the device.
+ samplerate: The software sampling rate of the device.

You cannot create more than one listener per device and likewise until a listener has been created for a device, you cannot run any of the device subcommands other than `devices add` for the indicated device.

Also note that when you add a device, its Listener will default to the `PAUSED` state. To start the Listener, type `devices resume [DEVICE]`. This will start the devices Listener which will report events at the sampling rate you provided when you intially added the device.

    
### Example Usage
Below is an example interaction with the client showing typical usage. Note that the `->` indicates the result of running the command.

```
SDCP: server connect 0.0.0.0:8080
-> Now uploading to server @ 0.0.0.0:8080.

SDCP: devices add /dev/ttyUSB0 57600 250
-> Added serial device @ /dev/ttyUSB0.

SDCP: devices resume /dev/ttyUSB0
-> Resuming listening on device /dev/ttyUSB0...

SDCP: devices show
-> DEVICE       BAUDRATE SAMPLERATE STATUS
-> /dev/ttyUSB0 56700    250        RUNNING

SDCP: devices stop /dev/ttyUSB0
-> Stopping listener on /dev/ttyUSB0...

SDCP: exit
```


## Requirements
This software employs the Python programming langauge and requires Python version 3.7+. In addition, this software requires the following additional Python software libraries:

+ [aiohttp](https://pypi.org/project/aiohttp/)
+ [click](https://pypi.org/project/click/)
+ [click-shell](https://pypi.org/project/click-shell/)
+ [config](https://pypi.org/project/config/)
+ [pyserial](https://pypi.org/project/pyserial/)
+ [tinyos](https://pypi.org/project/tinyos/)
