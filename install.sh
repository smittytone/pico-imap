#!/bin/bash

# Change is if you have changed the name of your CircuitPython drive
TARGET_PICO="/Volumes/CIRCUITPY"

# Copy required libraries
if [[ ! -e "${TARGET_PICO}/Lib" ]]; then
    mdkir "${TARGET_PICO}/Lib"
fi
cp ./HT16K33-Python/ht16k33.py "${TARGET_PICO}/Lib/ht16k33.py"
cp ./HT16K33-Python/ht16k33segment14.py "${TARGET_PICO}/Lib/ht16k33segment14.py"

# Copy application code
cp ./boot.py "${TARGET_PICO}/boot.py"
cp ./code.py "${TARGET_PICO}/code.py"