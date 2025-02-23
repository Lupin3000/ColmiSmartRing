import asyncio
from signal import signal, SIGINT
from types import FrameType
from typing import Optional
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from config.colmi_address import RING_NAME, RING_ADDRESS
from libs.packages import parse_real_time_reading, get_start_packet, get_continue_packet, get_stop_packet


RXTX_WRITE_CHARACTERISTIC_UUID: str = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
RXTX_NOTIFY_CHARACTERISTIC_UUID: str = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
MAX_MEASUREMENT: int = 5
REAL_TIME_SPO2: int = 3


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
    global values

    _ = sender
    spo2 = parse_real_time_reading(data)

    if spo2 is not None:
        values.append(spo2)
        print(f"[INFO] Blood oxygen saturation level: {spo2} %")
    else:
        print("[WARNING] Invalid data received. Skipping...")

    if len(values) >= MAX_MEASUREMENT:
        stop_event.set()


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
    global values

    print(f"[INFO] Connecting to {device_name} [{device_address}]...")

    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print(f"[ERROR] Failed to connect to {device_name} [{device_address}].")
            return

        print(f"[INFO] Connected to {device_name} [{device_address}].")

        start_packet = get_start_packet(REAL_TIME_SPO2)
        print(f"[INFO] Send start package: {start_packet.hex()}")
        await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, start_packet)
        await asyncio.sleep(0.5)

        continue_packet = get_continue_packet(REAL_TIME_SPO2)
        print(f"[INFO] Send continue package: {continue_packet.hex()}")
        await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, continue_packet)
        await client.start_notify(RXTX_NOTIFY_CHARACTERISTIC_UUID, handle_notification)

        print("[INFO] Wait for real-time spo2 data... (Stop with Ctrl + c)")

        try:
            await stop_event.wait()
        except KeyboardInterrupt:
            print("[INFO] Measurement is ended...")
        finally:
            stop_packet = get_stop_packet(REAL_TIME_SPO2)
            print("[INFO] Send Stop package:", stop_packet.hex())
            await client.write_gatt_char(RXTX_WRITE_CHARACTERISTIC_UUID, stop_packet)
            await client.stop_notify(RXTX_NOTIFY_CHARACTERISTIC_UUID)
            print("[INFO] Disconnected from device.")

            spo2_avg = sum(values) / len(values) if values else 0
            print(f"\n[INFO] Average Heart Rate: {int(spo2_avg)} %")


if __name__ == "__main__":
    values = []

    stop_event = asyncio.Event()
    signal(SIGINT, signal_handler)

    try:
        asyncio.run(main(device_name=RING_NAME, device_address=RING_ADDRESS))
    except KeyboardInterrupt:
        print("[INFO] Program interrupted by user.")
