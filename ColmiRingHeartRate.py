import asyncio
from signal import signal, SIGINT
from types import FrameType
from typing import Optional
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from config.colmi_address import RING_NAME, RING_ADDRESS


RXTX_WRITE_CHARACTERISTIC_UUID: str = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_NOTIFY_CHARACTERISTIC_UUID: str = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
CMD_START_REAL_TIME: int = 105
CMD_STOP_REAL_TIME: int = 106
ACTION_START: int = 1
ACTION_CONTINUE: int = 3
REAL_TIME_HEART_RATE: int = 1


stop_event = asyncio.Event()


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

    print(f"[INFO] Signal {sig} received. Exiting...")

    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(stop_event.set)


def make_packet(command: int, sub_data: Optional[bytearray] = None) -> bytearray:
    """
    Creates a data packet with a specified command and optional sub-data payload.

    :param command: A command value used to initialize the first byte of the packet.
    :type command: int
    :param sub_data: An optional sub-data payload to be included in the packet.
    :type sub_data: Optional[bytearray]
    :return: bytearray
    """
    assert 0 <= command <= 255, "[WARNING] Invalid command, must be between 0 and 255"

    packet = bytearray(16)
    packet[0] = command

    if sub_data:
        assert len(sub_data) <= 14, "[WARNING] Sub-data must be a maximum of 14 bytes long"

        for i in range(len(sub_data)):
            packet[i + 1] = sub_data[i]

    packet[-1] =  sum(packet) & 255

    return packet


def get_start_packet(reading_type: int) -> bytearray:
    """
    Generates the start packet for initiating real-time data reading with the given
    reading type.

    :param reading_type: The type of real-time data reading to initiate.
    :type reading_type: int
    :return: bytearray
    """
    return make_packet(CMD_START_REAL_TIME, bytearray([reading_type, ACTION_START]))


def get_continue_packet(reading_type: int) -> bytearray:
    """
    Constructs a packet for continuing real-time reading with a specific type.

    :param reading_type: Specifies the type of reading to continue.
    :type reading_type: int
    :return: bytearray
    """
    return make_packet(CMD_START_REAL_TIME, bytearray([reading_type, ACTION_CONTINUE]))


def get_stop_packet(reading_type: int) -> bytearray:
    """
    Generates a stop packet for the specified reading type.

    :param reading_type: Specifies the type of reading to stop.
    :type reading_type: int
    :return: bytearray
    """
    return make_packet(CMD_STOP_REAL_TIME, bytearray([reading_type, 0, 0]))


def parse_real_time_reading(packet: bytearray) -> Optional[int]:
    """
    Parses a real-time reading from the given bytearray packet.

    :param packet: Input bytearray packet to be analyzed.
    :type packet: bytearray
    :return: Extracted reading as an integer if parsing succeeds, otherwise None.
    :rtype: Optional[int]
    """
    if len(packet) < 4:
        return None

    if packet[0] != CMD_START_REAL_TIME:
        return None

    if packet[2] != 0:
        print(f"[WARNING] Incorrect package contents - code: {packet[2]}")
        return None

    return packet[3]


async def handle_notification(sender: BleakGATTCharacteristic, data: bytearray) -> None:
    """
    Handles and processes the received notification data from a Bluetooth Low Energy (BLE)
    device. Extracts real-time heart rate reading from the provided `data` and logs
    the information.

    :param sender: The BLE GATT characteristic that sent the notification.
    :type sender: BleakGATTCharacteristic
    :param data: A byte array containing the real-time reading to be parsed.
    :type data: bytearray
    :return: None
    """
    _ = sender
    hr = parse_real_time_reading(data)

    if hr is not None:
        print(f"[INFO] Heart rate: {hr} bpm")
    else:
        print("[WARNING] Invalid data received. Skipping...")


async def main(device_name: str, device_address: str) -> None:
    """
    Connects to a BLE (Bluetooth Low Energy) device and starts a real-time data transfer
    session for heart rate measurement. This function handles the connection, sending
    start/continue packets, enabling notifications, and stopping the session after
    a termination signal or interruption.

    :param device_name: Name of the BLE device.
    :type device_name: str
    :param device_address: MAC address of the BLE device.
    :type device_address: str
    :return: None
    """
    print(f"[INFO] Connecting to {device_name} [{device_address}]...")

    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print(f"[ERROR] Failed to connect to {device_name} [{device_address}].")
            return

        print(f"[INFO] Connected to {device_name} [{device_address}].")

        start_packet = get_start_packet(REAL_TIME_HEART_RATE)
        print(f"[INFO] Send start package: {start_packet.hex()}")
        await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, start_packet)
        await asyncio.sleep(0.5)

        continue_packet = get_continue_packet(REAL_TIME_HEART_RATE)
        print(f"[INFO] Send continue package: {continue_packet.hex()}")
        await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, continue_packet)
        await client.start_notify(RXTX_NOTIFY_CHARACTERISTIC_UUID, handle_notification)

        print("[INFO] Wait for real-time heart rate data... (Stop with Ctrl + c)")

        try:
            await stop_event.wait()
        except KeyboardInterrupt:
            print("[INFO] Measurement is ended...")
        finally:
            stop_packet = get_stop_packet(REAL_TIME_HEART_RATE)
            print("[INFO] Send Stop package:", stop_packet.hex())
            await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, stop_packet)
            await client.stop_notify(RXTX_NOTIFY_CHARACTERISTIC_UUID)
            print("[INFO] Disconnected from device.")


if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    try:
        asyncio.run(main(device_name=RING_NAME, device_address=RING_ADDRESS))
    except KeyboardInterrupt:
        print("[INFO] Program interrupted by user.")
