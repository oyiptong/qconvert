import os
from setuptools import setup, find_packages

setup(
    name="quick-convert",
    version="0.1.0",
    description="Quickly downsample an image and generate a base64 blob",
    author="Olivier Yiptong",
    packages=find_packages(),
    scripts=["scripts/quick.py", "bin/mozcjpeg", "bin/pngquant"],
)
