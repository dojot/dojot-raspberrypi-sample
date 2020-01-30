# Raspberry Pi 3 - Sense Hat to Dojot integration
## It's a demo environment using a raspberry pi 3 - sense hat on the Dojot IoT platform

This demo has the purpose of integrating a physical device to Dojot with the MQTT protocol and also to implement a secure connection using TLS. 

It's behavior is divided into two applications that are running in parallel:
1° The sensors (temperature, humidity and pressure) are periodically read and their data are published at a default interval.
2° Through a joystick it's possible to switch between two actuations on the device:
- Pressing up: Two eyes are plotted on the LED matrix, using an accelerometer sensor, according to the movement of the device the eyes change position and the movement data are published in real time on Dojot.
- Pressing down: A running machine is simulated, a red ball is going through the matrix at a default speed
- Pressing middle: Closes applications

You'll need:
* [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b)
* [Sense Hat](https://www.raspberrypi.org/products/sense-hat/)
* [Running instance of dojot platform](http://dojotdocs.readthedocs.io/en/latest/installation-guide.html)

You must configure your device before starting, run the commands:

```shell
sudo apt-get install sense-hat
pip3 install paho-mqtt
pip3 install requests
git clone https://github.com/MatheusTenorio/private-sensehat.git
cd private-sensehat
```
To execute the code it's necessary to pass some parameters: `Dojot Host`, `Raspberry IP` and `Port`
- Execute: 

```shell
python3 -m dojotsh.main -H <Dojot Host> -d <Raspberry IP> -P 8883 
```

The `dojotsh.main` script will configure dojot with the template `RaspberryPi-SenseHat` and the device `RaspberryPi`

The data will be available in dojot as illustrated in the image below.
![Raspberry Pi data received by Dojot](images/sensors.png)

Accelerometer application.
![Movement eyes](images/movement_actuation.jpg)
![Movement publish](images/movement_publish.png)

Running machine application.
![Running machine actuation](images/running-machine.jpg)


# GUI
A python graphical interface was also developed using lib Tkinter, it's used for the dojot actuation on the device, being able to change the publish time of the sensors and the time of the running machine.
To send Dojot data to the device, you need to fill in the fields with the correct data. The help button will help to fill them.

The interface is in the image below:
![Graphical Interface](images/GUI.png)

- Execute:

```shell
cd gui
sudo apt-get install python3-tk
sudo apt-get install python3-requests
python3 gui.py
```
