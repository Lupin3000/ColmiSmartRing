from typing import Optional


CMD_START_REAL_TIME: int = 105
CMD_STOP_REAL_TIME: int = 106
ACTION_START: int = 1
ACTION_CONTINUE: int = 3


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

    packet[-1] = sum(packet) & 255

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
