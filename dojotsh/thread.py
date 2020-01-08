# from threading import Thread
# from sense_hat import SenseHat
# from dojotsh.mqtt_client import Client
# from dojotsh.sensor import Sensor 
# import logging

# class dataSense:
#     def __init__(self):
#         self._running = True

#     def terminate(self):
#         print("Finish")
#         self._running = False

#     def run(self):
#         while self._running:
#             sensor = Sensor()
#             sensor.run()

# class dataClient:
#     def __init__(self):
#         self._running = True

#     def terminate(self):
#         print("Finish")
#         self._running = False

#     def run(self):
#         while self._running:
#             client = Client()
#             client.run()
