import re
import requests
import json
from OpenSSL import crypto

# this is a script with utility functions related to certificate files creation
# and EJBCA-REST requests


# the following functions are related to file manipulation
# these functions  may throw crypto.Error

def saveCRL(filename, rawCRL):
    crl = ("-----BEGIN X509 CRL-----\n"
           + re.sub("(.{64})", "\\1\n", rawCRL, 0, re.DOTALL)
           + "\n-----END X509 CRL-----\n")
    crypto.load_crl(crypto.FILETYPE_PEM, crl)

    with open(filename, "w") as crlFile:
        crlFile.write(crl)


def saveCRT(filename, rawCRT):
    crt = ("-----BEGIN CERTIFICATE-----\n"
           + rawCRT + "\n-----END CERTIFICATE-----\n")

    with open(filename, "w") as crtFile:
        crtFile.write(crt)


def generateCSR(CName, privateKeyFile, csrFileName,
                dnsname=[], ipaddr=[]):
    # based on https://github.com/cjcotton/python-csr
    ss = []
    if dnsname:
        for i in dnsname:
            ss.append("DNS:%s" % i)

    if ipaddr:
        for i in ipaddr:
            ss.append(b"IP: %s" % i)
    ss = ", ".join(ss)

    req = crypto.X509Req()
    req.get_subject().CN = CName

    # Add in extensions
    base_constraints = ([
        crypto.X509Extension(b"keyUsage", False,
                             b"Digital Signature, Non Repudiation, Key Encipherment"),
        crypto.X509Extension(b"basicConstraints", False, b"CA:FALSE"),
    ])
    x509_extensions = base_constraints

    if ss:
        san_constraint = crypto.X509Extension(b"subjectAltName", False, ss.encode())
        x509_extensions.append(san_constraint)

    req.add_extensions(x509_extensions)

    with open(privateKeyFile) as keyfile:
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, keyfile.read())

    req.set_pubkey(key)
    req.sign(key, "sha256")

    with open(csrFileName, "w") as csrFile:
        csrFile.write(
                        crypto.dump_certificate_request(crypto.FILETYPE_PEM,
                                                        req)
                        .decode("ascii")
                    )


def generatePrivateKey(keyFile, bitLen):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, bitLen)
    with open(keyFile, "w") as keyFile:
        keyFile.write(
                        crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
                        .decode("ascii")
                     )


# default header for HTTP requests
defaultHeader = {
                    'content-type': 'application/json',
                    'Accept': 'application/json'
                }


# the following functions are related to EJBCA-REST requests
# they may throw requests.exceptions.ConnectionError,
# KeyError or HTTPError

def retrieveCAChain(EJBCA_API_URL, caName):
    response = requests.get(EJBCA_API_URL + '/ca/' + caName,
                            headers=defaultHeader)
    response.raise_for_status()
    return response.json()['certificate']


def retrieveCACRL(EJBCA_API_URL, CAName):
    response = requests.get(EJBCA_API_URL + '/ca/' + CAName + "/crl",
                            headers=defaultHeader)
    response.raise_for_status()
    return response.json()['CRL']


def signCert(EJBCA_API_URL, csrFile, CName, passwd):
    with open(csrFile, "r") as csrFile:
        csr = csrFile.read()
    cutDownCSR = csr[
                        csr.find('-----BEGIN CERTIFICATE REQUEST-----')
                        + len('-----BEGIN CERTIFICATE REQUEST-----')
                        :csr.find("-----END CERTIFICATE REQUEST-----")
                    ].replace("\n", "")

    req = json.dumps({
        "passwd": passwd,
        "certificate": cutDownCSR
    })

    response = requests.post(EJBCA_API_URL + "/sign/" + CName + "/pkcs10",
                             headers=defaultHeader, data=req)
    response.raise_for_status()
    return response.json()['status']['data']
