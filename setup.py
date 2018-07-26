from setuptools import setup, find_packages
from os import path

setup(
    name='amb_sdk',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0',

    description='The AMB SDK is a python client for the AMB API.',

    # The project's main homepage.
    url='https://bitbucket.org/sparkcognition/amb-sdk',

    # Author details
    author='Sheila Cheng',
    author_email='scheng@sparkcognition.com',
    install_requires=[
        'requests',
        'validators',
        'urllib3',
        'pandas',
        'matplotlib',
        'scikit-learn',
        'scipy',
        'jupyter'
    ],
    packages=['amb_sdk']
)
