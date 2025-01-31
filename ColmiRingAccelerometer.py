import asyncio
from signal import signal, SIGINT
from types import FrameType
from typing import Optional
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from config.colmi_address import RING_NAME, RING_ADDRESS


RXTX_WRITE_CHARACTERISTIC_UUID: str = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_NOTIFY_CHARACTERISTIC_UUID: str = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


def create_command(hex_string: str) -> bytes:
    """
    Converts a hexadecimal string into a byte array command.

    :param hex_string: A hexadecimal string where each pair of characters represents a byte.
    :type hex_string: str
    :return: A `bytes` object representing the generated command.
    :rtype: bytes
    """
    bytes_array = [int(hex_string[i:i + 2], 16) for i in range(0, len(hex_string), 2)]

    while len(bytes_array) < 15:
        bytes_array.append(0)

    checksum = sum(bytes_array) & 0xFF
    bytes_array.append(checksum)

    return bytes(bytes_array)


ENABLE_RAW_SENSOR_CMD = create_command("a104")
DISABLE_RAW_SENSOR_CMD = create_command("a102")

stop_event = asyncio.Event()


def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
    """
    Handles operating system signals by logging a message and triggering an async
    event to gracefully stop the event loop.

    :param sig: The signal number received by the process.
    :type sig: int
    :param frame: Current stack frame information. Can be None.
    :type frame: Optional[FrameType]
    :return: None
    """
    _ = frame

    print(f"[INFO] Signal {sig} received. Exiting...")

    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(stop_event.set)


async def handle_notification(sender: BleakGATTCharacteristic, data: bytearray) -> None:
    """
    Handles notifications received from a BLE (Bluetooth Low Energy) characteristic.

    :param sender: The BLE characteristic that sent the notification.
    :type sender: BleakGATTCharacteristic
    :param data: The notification payload containing raw bytes to be processed.
    :type data: bytearray
    :return: None
    """
    _ = sender

    if len(data) >= 10 and data[0] == 0xA1 and data[1] == 0x03:
        acc_x = (
            ((data[6] << 4) | (data[7] & 0xF)) - (1 << 11) if data[6] & 0x8 else ((data[6] << 4) | (data[7] & 0xF))
        )
        acc_y = (
            ((data[2] << 4) | (data[3] & 0xF)) - (1 << 11) if data[2] & 0x8 else ((data[2] << 4) | (data[3] & 0xF))
        )
        acc_z = (
            ((data[4] << 4) | (data[5] & 0xF)) - (1 << 11) if data[4] & 0x8 else ((data[4] << 4) | (data[5] & 0xF))
        )
        print(f"X={acc_x}, Y={acc_y}, Z={acc_z}")


async def send_data_array(client: BleakClient, command: bytes, service_name: str) -> None:
    """
    Send an array of data to a BLE service using the provided client.

    :param client: The BLE client instance used to send the data. Must be an instance of BleakClient.
    :type client: BleakClient
    :param command: The data to be sent to the BLE service. Represented as a sequence of bytes.
    :type command: bytes
    :param service_name: The name of the BLE service to which the data is being sent.
    :type service_name: str
    :return: None
    """
    try:
        await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, command)
    except Exception as e:
        print(f"Failed to send data to {service_name} service: {e}")


async def main(device_name: str, device_address: str) -> None:
    """
    Establishes a connection to a BLE (Bluetooth Low Energy) device and facilitates
    communication by enabling notifications and sending commands.

    :param device_name: The name of the BLE device being connected to.
    :type device_name: str
    :param device_address: The MAC address or UUID of the BLE device.
    :type device_address: str
    :return: None
    """
    print(f"[INFO] Connecting to {device_name} [{device_address}]...")

    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print(f"[ERROR] Failed to connect to {device_name} [{device_address}].")
            return

        print(f"[INFO] Connected to {device_name} [{device_address}].")

        await client.start_notify(RXTX_NOTIFY_CHARACTERISTIC_UUID, handle_notification)

        await asyncio.sleep(2)

        await send_data_array(client, ENABLE_RAW_SENSOR_CMD, "RXTX")

        try:
            await stop_event.wait()
        finally:
            print("[INFO] Stopping device communication...")
            await send_data_array(client, DISABLE_RAW_SENSOR_CMD, "RXTX")
            print("[INFO] Disconnected from device.")


if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    try:
        asyncio.run(main(device_name=RING_NAME, device_address=RING_ADDRESS))
    except KeyboardInterrupt:
        print("[INFO] Program interrupted by user.")
