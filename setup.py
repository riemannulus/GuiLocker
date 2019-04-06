from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='guilocker',
    version='0.2.1',
    long_description=long_description,
    url='https://github.com/riemannulus/GuiLocker',
    author='Lee, Suho',
    author_email='riemannulus@hitagi.moe',
    license='MIT',
    packages=find_packages(),
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],

    keywords='GuiLocker BitLocker',
    scripts=['bin/guilocker'],
)
