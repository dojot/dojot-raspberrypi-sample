import logging
import sys
from threading import Thread
from optparse import OptionParser
from dojotsh.mqtt_client import Client
from dojotsh.sensor import Sensor
from dojotsh.create import DojotAgent
from certificateretriever.generateLoginPwd import Certs

# set logger
logger = logging.getLogger('raspberry-pi.dojot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - '
                              'Thread %(thread)d - %(levelname)s - '
                              '%(message)s')
channel = logging.StreamHandler()
channel.setFormatter(formatter)
logger.addHandler(channel)

if __name__ == '__main__':
    # parse arguments
    parser = OptionParser()

    # MQTT broker - IP
    parser.add_option("-H", "--host", dest="host", default="127.0.0.1",
                      help="MQTT host to connect to. Defaults to localhost.")

    # MQTT broker - Port
    parser.add_option("-P", "--port", dest="port", type="int", default=1883,
                      help="MQTT port to connect to. Defaults to 1883.")

    # dojot - Tenant ID
    parser.add_option("-t", "--tenant", dest="tenant", default="admin",
                      help="Tenant identifier in dojot. Defaults to admin.")

    # dojot - User ID
    parser.add_option("-u", "--user", dest="user", default="admin",
                      help="User identifier in dojot. Defaults to admin.")

    # dojot - User password
    parser.add_option("-p", "--password", dest="password", default="admin",
                      help="User password in dojot. Defaults to admin.")

    # dojot - https or http
    parser.add_option("-s", action="store_true", dest="secure", default=False,
                      help="Enables https communication with dojot.")

    # polling interval
    parser.add_option("-i", "--interval", dest="interval", type="int", default=15,
                      help="Polling interval in seconds. Defaults to 15.")

    # overwrite
    parser.add_option('-w', '--overwrite',
                       help='Overwrite any existing key or certificate',
                       action="store_true")

    # DNS
    parser.add_option('-d', '--dns', dest="dns",
                        help='A hostname for identify the device')

    # CANAME
    parser.add_option('-c', '--caname', type=str,
                        default='IOTmidCA', dest='caName',
                        help='Name of the CA to sign the certificate')
    # Key Length
    parser.add_option('-k', '--key-length', type=int,
                        default=2048, dest='keyLength',
                        help='Key length in bits')

    # skipHttpsVerification
    parser.add_option('--skip-https-check', action="store_false",
                        dest='skipHttpsVerification',
                        help='Will not validate dojot certificate (dangerous)')

    (options, args) = parser.parse_args()
    logger.info("Options: %s", str(options))

    create = DojotAgent(options.host,
                    options.port,
                    options.tenant,
                    options.user,
                    options.password,
                    options.secure)

    device_id = create._has_dojot_been_set()

    certs = Certs(options,
                device_id)

    certs.generateCerts()

    client = Client(options.host,
                options.port,
                options.tenant,
                device_id,
                options.interval)

    sensor = Sensor(client,
                    options.interval)

    # Set Thread sensor
    sensorDataThread = Thread(target=sensor.run)
    sensorDataThread.start()

    # Set Thread MQTT
    clientDataThread = Thread(target=sensor.runMeasures)
    clientDataThread.start()
