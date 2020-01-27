#!/usr/bin/python
#
import os
import sys
import binascii
from OpenSSL import crypto
from time import sleep
import requests
import getpass
import jwt
import logging
from certificateretriever import certUtils
from certificateretriever import conf

class Certs(object):
    def __init__(self, userConf, device_id):
        self._logger = logging.getLogger('raspberry-pi.dojot.agent')
        self.userConf = userConf
        self.device_id = device_id

    def dojotLogin(self, dojot, username, passwd, httpsVerify):
        # if not username:
        #     username = input('enter your dojot username: ')
        # passwd = getpass.getpass('enter password for ' + username + ': ')
        try:
            r = requests.post(dojot + conf.authpath, verify=httpsVerify,
                            json={
                                "username": username,
                                "passwd": passwd
                            })
            r.raise_for_status()
        except requests.exceptions.ConnectionError:
            self._logger.info("Could not connect to Auth service at " + dojot + conf.authpath)
            exit(-1)
        except requests.exceptions.HTTPError as err:
            self._logger.info('Authentication faied')
            if err.response.status_code in [403, 401]:
                self._logger.error('Wrong user or password')
            else:
                self._logger.error('Err code %d. mesage %s' %
                    (err.response.status_code, err.response.text))
            exit(-1)

        return r.json()['jwt']


    def generateKeys(self, devname, length, overwrite):
        filename = conf.certsDir + "/" + devname + ".key"
        if not os.path.isfile(filename) or overwrite:
            certUtils.generatePrivateKey(filename, length)
            self._logger.info(devname + " key pair created at " + filename)
        else:
            self._logger.info("Key pair already exists at " + filename + ". Skiping.")


    def generateCSR(self, devname, overwrite, dns, ip):
        filename = conf.certsDir + "/" + devname + ".csr"
        if not os.path.isfile(filename) or overwrite:
            certUtils.generateCSR(
                CName=devname,
                privateKeyFile=conf.certsDir + "/" + devname + ".key",
                csrFileName=filename,
                dnsname=dns, ipaddr=ip)
        else:
            self._logger.info("CSR file already exists at " + filename + ". Skiping.")


    def askCertSign(self, ejbcaHost, devname, overwrite):
        filename = conf.certsDir + "/" + devname + ".crt"
        if not os.path.isfile(filename) or overwrite:
            try:
                cert = certUtils.signCert(ejbcaHost,
                                        conf.certsDir + "/" + devname + ".csr",
                                        devname, 'dojot')
            except requests.exceptions.HTTPError as err:
                self._logger.info("Cant sign the CRT. EJBCA-REST return code: "
                    " EJBCA-REST return code: "
                    + str(err.response.status_code))
                self._logger.info(str(err.response.text))
                self.helperErrorDesc(err.response.status_code)
                exit(-1)
            certUtils.saveCRT(filename, cert)
            self._logger.info(devname + " certificate signed. Avaliable at " + filename)
        else:
            self._logger.info("Certificate file already exists at " + filename + ". Skiping.")


    def retrieveCAChain(self, ejbcaHost, caName, overwrite):
        filename = conf.certsDir + "/" + caName + ".crt"
        if not os.path.isfile(filename) or overwrite:
            try:
                rawCrt = certUtils.retrieveCAChain(ejbcaHost, caName)
                certUtils.saveCRT(filename, rawCrt)
                self._logger.info("CA certificates retrieved")
            except KeyError:
                self._logger.info("Invalid answer returned from EJBCA.")
                exit(-1)
            except requests.exceptions.HTTPError as err:
                self._logger.info("Can't retrieve CA chain certificate."
                    " EJBCA-REST return code: "
                    + str(err.response.status_code))
                self._logger.info(str(err.response.text))
                self.helperErrorDesc(err.response.status_code)
                exit(-1)
        else:
            self._logger.info("CA Certificate file already exists at "
                + filename + ". Skiping.")

    def retrieveCRL(self, ejbcaHost, caName):
        try:
            rawCRL = certUtils.retrieveCACRL(ejbcaHost, caName)
        except KeyError:
            self._logger.info("Invalid answer returned from EJBCA.")
            exit(-1)
        except requests.exceptions.HTTPError as err:
            self._logger.error("Can't retrieve CA CRL."
                            " EJBCA-REST return code: "
                + str(err.response.status_code))
            self._logger.info(str(err.response.text))
            self.helperErrorDesc(err.response.status_code)
            exit(-1)
        try:
            certUtils.saveCRL(conf.certsDir + "/" + caName + ".crl", rawCRL)
        except crypto.Error:
            self._logger.error("Could not decode retrieved CRL")
            exit(-1)

    def helperErrorDesc(self, code):
        if code == 401 or code == 403:
            self._logger.error("Your user is not allowed to do this")
        elif code == 500:
            self._logger.error("internal server error")
        elif code == 503:
            self._logger.error("Service unavailable. "
                "If you are using dojot, check if Kong is configurated,"
                " and if EJBCA-REST and Auth are running")
    
    def generateCerts(self):
        self._logger = logging.getLogger('raspberry-pi.dojot.agent')
        url = "http://{}:8000".format(self.userConf.host)

        userAuth = self.dojotLogin(url, self.userConf.user,
                            self.userConf.password,
                            self.userConf.skipHttpsVerification)
        self._logger.info('Authenticated')

        if not os.path.exists(conf.certsDir):
            os.makedirs(conf.certsDir)

        # get tenant from auth user
        tenant = (jwt.decode(userAuth, verify=False))['service']
        
        deviceName = tenant+':'+self.device_id

        certUtils.defaultHeader['Authorization'] = 'Bearer ' + userAuth

        self.retrieveCAChain(url, self.userConf.caName, self.userConf.overwrite)
       # self.retrieveCRL(self.userConf.dojot, self.userConf.caName)

        self.generateKeys(deviceName,
                    self.userConf.keyLength,
                    self.userConf.overwrite)
        self.generateCSR(deviceName,
                    self.userConf.overwrite,
                    self.userConf.dns, None)
        self.askCertSign(url, deviceName, self.userConf.overwrite)
