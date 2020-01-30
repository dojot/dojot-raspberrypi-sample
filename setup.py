# -*- coding: utf-8 -*-
# https://pythonhosted.org/versiontools/usage.html
from setuptools import setup, find_packages


setup(
    name="dojot-sense-hat",
    description='Integration of raspberry pi sense hat with dojot platform.',
    version='1.0.0',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'paho-mqtt',
        'requests',
        'sense_hat'
    ],
    python_requires='>=3.0.0',
    author='Matheus Tenório Resende Ricaldoni',
    author_email='mresende@cpqd.com.br',
    url='https://github.com/MatheusTenorio/',
)
