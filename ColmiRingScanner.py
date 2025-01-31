from asyncio import run
from pathlib import Path
from signal import signal, SIGINT
from sys import exit
from types import FrameType
from typing import Optional
from bleak import BleakScanner
from bleak.backends.device import BLEDevice


TARGET_FOLDER: str = "config"
FILE_NAME: str = "colmi_address.py"
TEMPLATE: str = 'RING_NAME: str = ""\nRING_ADDRESS: str = ""\n'
SCAN_TIMEOUT: int = 10


def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
    """
    Handles the received signal, logs it, and raises a KeyboardInterrupt to
    terminate the execution.

    :param sig: The signal number received by the handler.
    :type sig: int
    :param frame: The current stack frame at the point the signal was received.
    :type frame: Optional[FrameType]
    :return: None
    """
    _ = frame

    print(f'[INFO] Signal handler: {sig} triggered. Exiting...')
    raise KeyboardInterrupt


def ensure_directory(directory_path: Path) -> None:
    """
    Ensures that a given directory exists. If the directory does not exist, it is created,
    including all necessary parent directories.

    :param directory_path: A Path object representing the directory to be checked or created.
    :type directory_path: Path
    :return: None
    :raises IOError: If the directory cannot be created due to an error.
    """
    if not directory_path.exists():
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
        except IOError as err:
            print(f'[ERROR] Failed to create directory: {err}')


def update_config_file(file_path: Path, name: str, address: str) -> None:
    """
    Create/updates the configuration file with the given device name and address.

    :param file_path: The path of the configuration file.
    :type file_path: Path
    :param name: The name of the BLE device.
    :type name: str
    :param address: The address of the BLE device.
    :type address: str
    :return: None
    :raises IOError: If the configuration file cannot be created/updated due to an error.
    """
    content = f'RING_NAME: str = "{name}"\nRING_ADDRESS: str = "{address}"\n'
    try:
        file_path.write_text(content)
    except IOError as err:
        print(f'[ERROR] Failed to update configuration file: {err}')


async def select_device(max_timeout: int = SCAN_TIMEOUT) -> Optional[BLEDevice]:
    """
    Asynchronously scans for BLE devices within a specified timeout period and allows the
    user to select a device from the discovered list. If no devices are found or the user
    interrupts the process, the function returns None.

    :param max_timeout: The timeout duration in seconds for scanning BLE devices.
    :type max_timeout: int
    :return: Returns a BLEDevice object if a valid choice was made, otherwise returns None.
    :rtype: Optional[BLEDevice]
    :raises ValueError: If the user enters an invalid choice.
    """
    try:
        print(f"[INFO] Scanning {max_timeout} seconds for BLE devices...")
        devices = await BleakScanner.discover(timeout=max_timeout)
        filtered_devices = [device for device in devices if device.name]

        if not filtered_devices:
            print("[WARNING] No BLE devices found.")
            return None

        for num, device in enumerate(filtered_devices):
            print(f"{num}: {device.name} [{device.address}]")

        try:
            choice = int(input("[ACTION] Insert number for Colmi Ring and press ENTER: "))
            if 0 <= choice < len(filtered_devices):
                return filtered_devices[choice]
            else:
                print(f"[ERROR] Please enter a valid number between 0 and {len(filtered_devices) - 1}.")
                return None
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")
            return None

    except KeyboardInterrupt:
        raise

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    current_file_path = Path(__file__).resolve().parent
    target_directory = current_file_path / TARGET_FOLDER
    target_file_path = target_directory / FILE_NAME

    ensure_directory(target_directory)

    try:
        selected_device = run(select_device())

        if not selected_device:
            print("[ERROR] No BLE device selected.")
            exit(1)
        else:
            device_name = selected_device.name
            device_address = selected_device.address
            update_config_file(target_file_path, device_name, device_address)
            print(f'[INFO] Saved device "{device_name}" with address "{device_address}".]')
    except KeyboardInterrupt:
        print("[INFO] Program interrupted by user.")
    finally:
        exit(0)