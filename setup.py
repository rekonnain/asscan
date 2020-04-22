# -*- coding: utf-8 -*-

from setuptools import setup

setup(
   name='asscan',
   version='0.1',
   description='ASSCAN - Automated Subnet Scanner',
   author='Ossi Väänänen',
   author_email='< ossi at disobey d0+ fi >',
   packages=['asscan'],  #same as name
   install_requires=['tornado', 'webscreenshot'], #external packages as dependencies
)