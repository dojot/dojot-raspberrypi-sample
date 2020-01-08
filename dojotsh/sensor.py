from sense_hat import SenseHat
import time
import logging
import json

class Sensor (object):
    def __init__(self, client):
        self._sense = SenseHat()
        self.client = client
        self.client.subscribe()
        self._pub = False
        self.pubfreq = 10
        self._logger = logging.getLogger('raspberry-pi.dojot.agent')
        w = (150, 150, 150)
        b = (0, 0, 255)
        e = (0, 0, 0)

        self.imageMiddle = [
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            w,w,w,e,e,w,w,w,
            w,b,w,e,e,w,b,w,
            w,w,w,e,e,w,w,w,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e
            ]
        self.imageRight = [
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            w,w,w,e,e,w,w,w,
            w,w,b,e,e,w,w,b,
            w,w,w,e,e,w,w,w,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e
            ]
        self.imageLeft = [
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            w,w,w,e,e,w,w,w,
            b,w,w,e,e,b,w,w,
            w,w,w,e,e,w,w,w,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e
            ]
        self.imageUp = [
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            w,b,w,e,e,w,b,w,
            w,w,w,e,e,w,w,w,
            w,w,w,e,e,w,w,w,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e
            ]
        self.imageDown = [
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            w,w,w,e,e,w,w,w,
            w,w,w,e,e,w,w,w,
            w,b,w,e,e,w,b,w,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e,
            e,e,e,e,e,e,e,e
            ]

    def _read_sensors(self):
        self._logger.info("Getting Temperature ...")
        temperature = round(self._sense.temperature,1)
        self._logger.info("Getting Humidity ...")
        humidity = round(self._sense.humidity,1)
        self._logger.info("Getting Pressure ...")
        pressure = round(self._sense.pressure,1)

        acceleration = self._sense.get_accelerometer_raw()
        x = acceleration['x']
        y = acceleration['y']
        z = acceleration['z']

        x = round(x,0)
        y = round(y,0)
        z = round(z,0)

        if (x==0.0 and y==0.0 and z==1.0):
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

        x = round(x,0)
        y = round(y,0)
        z = round(z,0)

        return x, y, z

    def run(self):
        while True:
            x, y, z = self._read_accelerometer()

            if (x==0.0 and y==0.0 and z==1.0):
                self._sense.set_pixels(self.imageMiddle)
            elif(x==0.0 and y==1.0 and z==0.0):
                self._sense.set_pixels(self.imageUp)
                message = "Looking Up"
                self.client.alert(message)
            elif(x==0.0 and y==-1.0 and z==0.0):
                self._sense.set_pixels(self.imageDown)
                message = "Looking Down"
                self.client.alert(message)
            elif(x==-1.0 and y==0.0 and z==0.0): 
                self._sense.set_pixels(self.imageRight)
                message = "Looking Right"
                self.client.alert(message)
            elif(x==1.0 and y==0.0 and z==0.0): 
                self._sense.set_pixels(self.imageLeft)
                message = "Looking Left"
                self.client.alert(message)
            
            #self.client.subscribe()
            time.sleep(0.5)
    
    def setTimer(self, time):
        self.pubfreq = time
        print("*********************************************************************")
        print(self.pubfreq)
        print("*********************************************************************")

    
    def runMeasures(self):
        while True:
            temperature, humidity, pressure, alert = self._read_sensors()
          #  speed = self.client._on_command()
            data = {'temperature': temperature,
                    'humidity': humidity,
                    'pressure': pressure}
            
            self.client.publish(json.dumps(data))
            time.sleep(self.pubfreq)