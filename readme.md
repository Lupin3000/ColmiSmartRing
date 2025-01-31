# Colmi Smart Ring - Python

## Installation

> The following Python code is developed with Python version: 3.12.x. Python bleak and asyncio are used for BLE communication. Tested with Colmi Smart Ring R06.

1. Clone this repository
2. Create Python virtualenv (_recommended_)
3. Install Python modules/packages

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
(.venv) $ python ColmiRingScanner.py
```

Sometimes the scanner will not find the Colmi Smart Ring, please try again! If you found the Colmi Smart Ring and selected it. The Python script will create a new directory (_config_). Inside this newly created directory a new file is created (_colmi_address.py_) with two constants (_RING_NAME and RING_ADDRESS_). These constants are used later by all other Python scripts.

## Read data from Colmi Smart Ring

### Accelerometer

> This Python script will read and print continuously the data and does not stop by itself! To stop press keys: Ctrl + c

```shell
# read accelerometer data 
(.venv) $ python ColmiRingAccelerometer.py
```

Sometimes the BLE connection will not be established, please try again!
