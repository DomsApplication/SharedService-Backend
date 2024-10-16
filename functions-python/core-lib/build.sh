#!/bin/bash

# Create a directory for the python package
mkdir -p build-lib/python

# Copy the core-lib directory to the python/ folder
cp -r core-lib/ build-lib/python/
cp -r requirements.txt build-lib/
cp -r README.md build-lib/

cd build-lib

# Install dependencies into the python/ directory
pip install -r requirements.txt -t python/

# Zip the contents
# For MS winods -10 powe shell command is : Compress-Archive -Path python\* -DestinationPath core-lib-layer.zip
zip -r core-lib-layer.zip python/

# Clean up
rm -rf python/
