import json
import time
import paho.mqtt.client as mqtt
from dojotsh.sensor import Sensor 
import logging
import sys
import ssl
import functools

class CertificateError(ValueError):
    pass
                                                                                                                                                                        
old_match_hostname = ssl.match_hostname

@functools.wraps(old_match_hostname)
def match_hostname_bugfix(cert, hostname):
    if cert['subjectAltName'][0][1] == hostname:
        return
    else:
        print("*******************************")
        print(cert['subjectAltName'])
        raise CertificateError("Hostname don't match!")

ssl.match_hostname = match_hostname_bugfix

class Client (object):
    def __init__(self, host: str, port: int, tenant: str, device_id: str, interval: int):
        self.host = host
        self.port = port
        self.tenant = tenant
        self.device_id = device_id
        self.message = ""
        self.certs_dir = "./certs"
        self.interval = interval
        self.is_connected = False

        self.ca_cert="{}/IOTmidCA.crt".format(self.certs_dir)
        self.cert_file="{}/{}:{}.crt".format(self.certs_dir, self.tenant, self.device_id)
        self.key_file="{}/{}:{}.key".format(self.certs_dir, self.tenant, self.device_id)
        self.client_id = "{}:{}".format(self.tenant, self.device_id)
        self.pub_topic = "/{}/{}/attrs".format(self.tenant, self.device_id)
        self.sub_topic = "/{}/{}/config".format(self.tenant, self.device_id)

        self._logger = logging.getLogger('raspberry-pi.dojot.agent')

        self._mqttc = mqtt.Client(self.client_id)
        self._mqttc.tls_set(ca_certs=self.ca_cert, certfile=self.cert_file, keyfile=self.key_file, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        self._mqttc.tls_insecure_set(False)
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect
        self._mqttc.on_message = self._on_message
        self._mqttc.on_publish = self._on_publish
        self._mqttc.on_subscribe = self._on_subscribe
        self._mqttc.connect(host=self.host, port=self.port)
        self._mqttc.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected!")
     #   print("Connected with results code", str(rc))
        self.is_connected = True

    def _on_message(self, client, userdata, message):
        print(message.topic, str(message.payload))

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(granted_qos)

    def _on_publish(self, client, userdata, mid):
        self._logger.info("Publish success")
      #  print("Publish success")

    def _on_disconnect(self, client, userdata, rc):
        self._logger.info("Disconnected, Reconnecting...")
      #  print("Disconnected, Reconnecting...")
        self.is_connected = False
        self._mqttc.reconnect()
    
    def alert(self, message):
        if(self.is_connected):
            data = {"message":message}
            self._logger.info("Publishing Alert!" + str(message))
            self._mqttc.publish(self.pub_topic, json.dumps(data))
        else: self._logger.info("Client not connected")

    def publish(self, message):
        if(self.is_connected):
            self._mqttc.publish(self.pub_topic, message)
            self._logger.info("Publishing " + str(message))
        else: self._logger.info("Client not connected")

    def subscribe(self, callback):
        self._logger.info("Subscribing to topic %s", self.sub_topic)
        self._mqttc.subscribe(self.sub_topic)
        self._mqttc.message_callback_add(self.sub_topic, callback)