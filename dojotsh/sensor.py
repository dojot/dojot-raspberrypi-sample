from sense_hat import SenseHat
import time
import logging
import json


class Sensor (object):
    def __init__(self, client, interval):
        self._sense = SenseHat()
        self.client = client
        self.client.subscribe(self._on_command)
        self._pubTimer = interval
        self._pubMove = 1
        self._pub = False
        self.press = ""
        self.exit = True
        self._logger = logging.getLogger('raspberry-pi.dojot.agent')
        self._sense.clear()
        w = (255, 255, 255)
        b = (0, 0, 255)
        e = (0, 0, 0)
        g = (0, 0, 0)

        self.imageMiddle = [
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            w, w, w, e, e, w, w, w,
            w, b, w, e, e, w, b, w,
            w, w, w, e, e, w, w, w,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e
            ]
        self.imageRight = [
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            w, w, w, e, e, w, w, w,
            w, w, b, e, e, w, w, b,
            w, w, w, e, e, w, w, w,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e
            ]
        self.imageLeft = [
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            w, w, w, e, e, w, w, w,
            b, w, w, e, e, b, w, w,
            w, w, w, e, e, w, w, w,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e
            ]
        self.imageUp = [
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            w, b, w, e, e, w, b, w,
            w, w, w, e, e, w, w, w,
            w, w, w, e, e, w, w, w,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e
            ]
        self.imageDown = [
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            w, w, w, e, e, w, w, w,
            w, w, w, e, e, w, w, w,
            w, b, w, e, e, w, b, w,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e,
            e, e, e, e, e, e, e, e
            ]
        self.treadmill = [
            g, g, g, g, g, g, g, g,
            g, g, g, g, g, g, g, g,
            w, w, w, w, w, w, w, w,
            w, w, w, w, w, w, w, w,
            g, g, g, g, g, g, g, g,
            w, w, w, w, w, w, w, w,
            w, w, w, w, w, w, w, w,
            g, g, g, g, g, g, g, g
        ]

    def _read_sensors(self):
        self._logger.info("Getting Temperature ...")
        temperature = round(self._sense.temperature, 1)
        self._logger.info("Getting Humidity ...")
        humidity = round(self._sense.humidity, 1)
        self._logger.info("Getting Pressure ...")
        pressure = round(self._sense.pressure, 1)

        acceleration = self._sense.get_accelerometer_raw()
        x = acceleration['x']
        y = acceleration['y']
        z = acceleration['z']

        x = round(x, 0)
        y = round(y, 0)
        z = round(z, 0)

        if (x == 0.0 and y == 0.0 and z == 1.0):
            self._pub = False
        else:

            self._pub = True

        return temperature, humidity, pressure, self._pub

    def _read_accelerometer(self):
        self._logger.info("Getting Movement")
        acceleration = self._sense.get_accelerometer_raw()
        x = acceleration['x']
        y = acceleration['y']
        z = acceleration['z']

        x = round(x, 0)
        y = round(y, 0)
        z = round(z, 0)

        return x, y, z

    def joystick(self):
        for self.event in self._sense.stick.get_events():
            if(self.event.action == "pressed"):
                if(self.event.direction == "up"):
                    press = self.event.direction
                elif(self.event.direction == "down"):
                    press = self.event.direction
                if(self.event.direction == "middle"):
                    self._logger.info("Sensor Stopped")
                    press = self.event.direction
                    self._sense.clear()
                return press

    def run(self):
        while True:
            self.press = self.joystick()
            if(self.press == "up"):
                self.exit = False
                self._sense.clear()
                self.press = ""
                while (self.exit == False):
                    x, y, z = self._read_accelerometer()
                    self.press = self.joystick()
                    if(self.press == "middle"):
                        self.exit = True
                    elif (x == 0.0 and y == 0.0 and z == 1.0):
                        self._sense.set_pixels(self.imageMiddle)
                    elif(x == 0.0 and y == 1.0 and z == 0.0):
                        self._sense.set_pixels(self.imageUp)
                        message = "Looking Up"
                        self.client.alert(message)
                    elif(x == 0.0 and y == -1.0 and z == 0.0):
                        self._sense.set_pixels(self.imageDown)
                        message = "Looking Down"
                        self.client.alert(message)
                    elif(x == -1.0 and y == 0.0 and z == 0.0):
                        self._sense.set_pixels(self.imageRight)
                        message = "Looking Right"
                        self.client.alert(message)
                    elif(x == 1.0 and y == 0.0 and z == 0.0):
                        self._sense.set_pixels(self.imageLeft)
                        message = "Looking Left"
                        self.client.alert(message)
                    time.sleep(0.5)
            elif (self.press == "down"):
                self._logger.info("Monitoring Speed")
                self.exit = False
                self._sense.clear()
                self._sense.set_pixels(self.treadmill)
                i = 0
                while(self.exit == False):
                    self.press = self.joystick()
                    if(self.press == "middle"):
                        self.exit = True
                    self._sense.set_pixel(i, 4, (200, 0, 0))
                    i += 1
                    time.sleep(self._pubMove)
                    if(i > 0):
                        self._sense.set_pixel(i-1, 4, (0, 0, 0))
                    if(i == 8):
                        i = 0

    def runMeasures(self):
        while True:
            temperature, humidity, pressure, alert = self._read_sensors()
            data = {'temperature': temperature,
                    'humidity': humidity,
                    'pressure': pressure}

            self.client.publish(json.dumps(data))
            time.sleep(self._pubTimer)

    def _on_command(self, _mqttc, _obj, msg):
        try:
            command = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            self._logger.error("Command is not coded a JSON")
            return
        self._logger.info("Received command %s", command)

        if ('pubTimer' in command):
            self._pubTimer = command['pubTimer']
            self._logger.info("Received message " + str(self._pubTimer))
        if ('pubMove' in command):
            self._pubMove = command['pubMove']
            self._logger.info("Received message " + str(self._pubMove))
