## Raspberry Pi 3 - Sense Hat to Dojot integration
# It's a demo environment using a raspberry pi 3 - sense hat on the Dojot IoT platform

This project has the purpose of integrating a physical device to Dojot with the MQTT protocol. 

You'll need:
* [Raspberry Pi 3] (https://www.raspberrypi.org/products/raspberry-pi-3-model-b)
* [Sense Hat] (https://www.raspberrypi.org/products/sense-hat/)
* [Running instance of dojot platform] (http://dojotdocs.readthedocs.io/en/latest/installation-guide.html)

DEVICE
1º Passo:
```shell
sudo apt-get update
sudo apt-get install sense-hat
pip3 install paho-mqtt
pip3 install requests
git clone ...
cd diretório
```

- execute: 
python3 -m dojotsh.main -H"<host da Dojot>" -d "<IP da raspberry>" -P 8883 

GUI
- execute:
sudo apt-get install python3-tk
sudo apt-get install python3-requests
python3 gui.py


Não estou usando: parseArgs.py, agent.py, __init__.py