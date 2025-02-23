# Colmi Smart Ring - Python

## Minimum requirements

[![Static](https://img.shields.io/badge/python->=3.12.x-green)](https://python.org)
[![Static](https://img.shields.io/badge/asyncio-==3.4.3-green)](https://docs.python.org/dev/library/asyncio.html)
[![Static](https://img.shields.io/badge/bleak-==0.22.3-green)](https://bleak.readthedocs.io/en/latest/)

## Installation

> Tested with Colmi Smart Ring R06 (_but should work with mostly all Colmi Smart Rings_).

1. Clone this repository
2. Create Python virtualenv (_recommended_)
3. Install required Python modules/packages (_via requirements.txt_)

```shell
# clone repository
$ git clone https://github.com/Lupin3000/ColmiSmartRing.git

# change into cloned directory
$ cd ColmiSmartRing/

# create virtualenv
$ python -m venv .venv

# activate virtual environment
$ .venv/bin/activate

# update pip (optional)
(.venv) $ pip3 install -U pip

# show content of requirements.txt (optional)
(.venv) $ cat requirements.txt

# install all modules/packages
(.venv) $ pip3 install -r requirements.txt

# list all modules/packages (optional)
(.venv) $ pip3 freeze
```

## Scan for Colmi Smart Ring

> To use all Python scripts, you need the BLE address of your Colmi Smart Ring!

```shell
# scan for smart ring address
(.venv) $ python3 ColmiRingScanner.py
```

Sometimes the scanner will not find the Colmi Smart Ring, please try again! If you found the Colmi Smart Ring and selected it. The Python script will create a new directory (_config_). Inside this newly created directory a new file is created (_colmi_address.py_) with two constants (_RING_NAME and RING_ADDRESS_). These constants are used later by all other Python scripts.

## Read data from Colmi Smart Ring

**Note:** Sometimes the BLE connection will not be established on first run, just try the respective Python script again.

### Accelerometer

> This Python script will read and print continuously the data from accelerometer (_X, Y, Z_).
>> To stop the script and BLE connection press keys: [Ctrl] + [c].

```shell
# read accelerometer data 
(.venv) $ python3 ColmiRingAccelerometer.py
```

### Real-time Heart Rate

> This Python script will read max. 5 values and print the average data for heart-rate (_bpm_).
>> To stop the script and BLE connection press keys: [Ctrl] + [c].

```shell
# read heart rate data 
(.venv) $ python3 ColmiRingHeartRate.py
```

### Real-time SpO2

> This Python script will read max. 5 values and print the average data for SpO2 (_%_).
>> To stop the script and BLE connection press keys: [Ctrl] + [c].

```shell
# read SpO2 data 
(.venv) $ python3 ColmiRingSPO2.py
```
