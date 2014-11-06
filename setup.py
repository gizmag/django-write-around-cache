#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-write-around-cache',
    version='0.1.0',
    description="Override Django's template cache at will",
    author='Gizmag',
    author_email='tech@gizmag.com',
    url='https://github.com/gizmag/django-write-around-cache',
    packages=find_packages(),
    install_requires=['django']
)
