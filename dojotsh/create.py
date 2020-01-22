import time
import logging
import requests
import json
import paho.mqtt.client as mqtt


class DojotAgent (object):

    def __init__(self, host, port, gw, tenant, user, password, secure):
        # set logger
        self._logger = logging.getLogger('raspberry-pi.dojot.agent')

        # keep connection parameters
        self._host = host
        self._port = port
        self._gw = gw
        self._tenant = tenant
        self._user = user
        self._password = password
        self._secure = secure

        # get raspberry pi serial number
        self._hw_serial = self._get_raspberry_pi_serial()

        # dojot jwt token
        self._logger.info("Getting JWT Token ...")
        if self._secure:
            url = 'https://{}/auth'.format(self._gw)
        else: url = 'http://{}:8000/auth'.format(self._gw)

        data = {"username": "{}".format(self._user),
                "passwd": "{}".format(self._password)}

        response = requests.post(url=url, json=data)
        if (response.status_code != 200):
            self._logger.error("HTTP POST to get JWT token failed (%s)", response.status_code)
            raise Exception("HTTP POST FAILED {}".format(response.status_code))
        
        self._token = response.json()['jwt']
        self._auth_header = {"Authorization": "Bearer {}".format(self._token)} 
        self._logger.info("Got JWT token %s", self._token)

        # dojot device ID
        self._device_id = self._has_dojot_been_set()

        # create template and device
        if (self._device_id is None):
            self._set_raspberry_pi_in_dojot()


    def _has_dojot_been_set(self):
        # check whether raspberry has been set in dojot
        if self._secure:
            url = 'https://{}/device'.format(self._gw)
        else: url = 'http://{}:8000/device'.format(self._gw)

        response = requests.get(url=url, headers=self._auth_header)
        if (response.status_code != 200):
            raise Exception("HTTP POST failed {}.".format(response.status_code))
        all_devices = list(response.json()['devices'])

        for dev in all_devices:
            if dev['label'] == 'RaspberryPi':
                return dev['id']
                
        return None

    def _get_raspberry_pi_serial(self):
        serial = "UNKNOWN000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    serial = line[10:26]
            f.close()
        except (OSError, IOError):
            self._logger.error("Cannot read /proc/cpuinfo")
            raise Exception("Cannot read /proc/cpuinfo")

        return serial

    def _set_raspberry_pi_in_dojot(self):
        # create template
        self._logger.info("Creating raspberry-pi template in dojot ...")
        time.sleep(2)
        if self._secure:
            url = 'https://{}/template'.format(self._gw)
        else: url = 'http://{}:8000/template'.format(self._gw)

        data = {"label": "RaspberryPi-SenseHat",
                "attrs": [{"label": "protocol",
                           "type": "meta",
                           "value_type": "string",
                           "static_value": "mqtt"},
                          {"label": "temperature",
                           "type": "dynamic",
                           "value_type": "float"},
                          {"label": "humidity",
                           "type": "dynamic",
                           "value_type": "float"},
                          {"label": "pressure",
                           "type": "dynamic",
                           "value_type": "float"},
                          {"label": "message",
                           "type": "dynamic",
                           "value_type": "string"},
                          {"label": "pubTimer",
                           "type": "actuator",
                           "value_type": "float"},
                           {"label": "pubMove",
                           "type": "actuator",
                           "value_type": "float"},
                          {"label": "serial",
                           "type": "static",
                           "value_type": "string",
                           "static_value": "undefined"}
                          ]}

        response = requests.post(url=url, headers=self._auth_header, json=data)
        if response.status_code != 200:
            self._logger.error("HTTP POST to create template failed (%s).", response.status_code)
            raise Exception("HTTP POST failed {}.".format(response.status_code))

        template_id = response.json()['template']['id']
        self._logger.info("Created template %s", template_id)

        # create device
        self._logger.info("Creating raspberry-pi device in dojot ...")
        if self._secure:
            url = 'https://{}/device'.format(self._gw)
        else: url = 'http://{}:8000/device'.format(self._gw)

        data = {"templates": ["{}".format(template_id)],
                "label": "RaspberryPi"}
        response = requests.post(url=url, headers=self._auth_header, json=data)
        if response.status_code != 200:
            self._logger.error("HTTP POST to create device failed (%s).", response.status_code)
            raise Exception("HTTP POST failed {}.".format(response.status_code))

        self._device_id = response.json()['devices'][0]['id']
        self._logger.info("Created device %s", self._device_id)

        # set serial number
        if self._secure:
            url = 'https://{}/device/{}'.format(self._gw, self._device_id)
        else: url = 'http://{}:8000/device/{}'.format(self._gw, self._device_id)

        # Get
        response = requests.get(url=url, headers=self._auth_header)
        if response.status_code != 200:
            raise Exception("HTTP POST failed {}.".format(response.status_code))

        data = response.json()
        attrs_static = []
        for attribute in data['attrs']["{}".format(template_id)]:
            if attribute['type'] == 'static':
                if attribute['label'] == 'serial':
                    attribute['static_value'] = self._hw_serial
                attrs_static.append(attribute)
        data['attrs'] = attrs_static

        # Put
        response = requests.put(url=url, headers=self._auth_header, json=data)
        if response.status_code != 200:
            raise Exception("HTTP POST failed {}.".format(response.status_code))

        return self._device_id
