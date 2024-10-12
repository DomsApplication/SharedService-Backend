#!/bin/bash

# Create a directory for the python package
mkdir -p build-lib/python

# Copy the core_lib directory to the python/ folder
cp -r core_lib/ build-lib/python/
cp -r requirements.txt build-lib/
cp -r README.md build-lib/

cd build-lib

# Install dependencies into the python/ directory
pip install -r requirements.txt -t python/

# Zip the contents
zip -r core-lib-layer.zip python/

# Clean up
rm -rf python/
