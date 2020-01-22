# This file parse the command line argumments

import argparse


def parseArgs():
    parser = argparse.ArgumentParser(description='Create key pair for a device'
                                     'and retrieve'
                                     ' a signed certificate from EJBCA-REST')

    parser.add_argument('dojot', metavar='Host', type=str,
                        help='HTTPS URL where dojot service can be found')

    parser.add_argument('deviceName', metavar='devn', type=str,
                        help='Name of the device the key '
                        'and certificate should be created')
                        
    parser.add_argument('-ca', '--caname', type=str,
                        default='IOTmidCA', dest='caName',
                        help='Name of the CA to sign the certificate')

    parser.add_argument('-u', '--username',
                        help='Your Dojot username')

    parser.add_argument('-w', '--overwrite',
                        help='Overwrite any existing key or certificate',
                        action="store_true")

    parser.add_argument('-d', '--dns',
                        help='A hostname for identify the device',
                        action="append")

    parser.add_argument('-i', '--ip',
                        help='A IP address where the device can be found',
                        action="append")

    parser.add_argument('-k', '--key-length', type=int,
                        default=2048, dest='keyLength',
                        help='Key length in bits')

    parser.add_argument('--skip-https-check', action="store_false",
                        dest='skipHttpsVerification',
                        help='Will not validate dojot certificate (dangerous)')

    args = parser.parse_args()
    return args
