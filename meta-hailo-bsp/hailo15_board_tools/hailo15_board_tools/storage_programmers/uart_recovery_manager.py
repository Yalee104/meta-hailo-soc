import serial
import time
from enum import Enum

from hailo15_board_tools.storage_programmers.storage_programmer import StorageProgrammer, logger

FIRMWARE_VERSION_MAJOR = 1
FIRMWARE_VERSION_MINOR = 4

EMMC_BLOCK_SIZE = 0x200

baudrates_dictionary = {57600: 1, 115200: 2, 230400: 3, 460800: 4, 576000: 5, 921600: 6}


class UartRecoveryDevice(Enum):
    FLASH = "flash"
    SDIO0 = "sdio0"
    SDIO1 = "sdio1"


class UartRecoveryCommunicator:

    FW_VERSION_OPCODE = 0x0
    JEDEC_OPCODE = 0x1
    WRITE_OPCODE = 0x2
    READ_OPCODE = 0x3
    ERASE_SECTOR_OPCODE = 0x4
    JUMP_BOOTROM_OPCODE = 0x5
    ERASE_CHIP_OPCODE = 0x6
    CHOOSE_STORAGE_OPCODE = 0x7
    WORK_WITH_FLASH_OPCODE = 0x8
    WORK_WITH_EMMC_OPCODE = 0x9
    SET_BAUDRATE_OPCODE = 0xA
    UART_BAUDRATE = 115200
    UART_TIMEOUT = 2  # seconds
    JEDEC_ID_LENGTH = 4
    ERASE_SECTOR_END_ACK = 0x55
    ERASE_CHIP_END_ACK = 0x56
    WRITE_END_ACK = 0x57

    def __init__(self, serial_device_name):
        self.serial_device_name = serial_device_name

    def open_serial(self):
        self._serial = serial.Serial(self.serial_device_name, self.UART_BAUDRATE, timeout=self.UART_TIMEOUT)

    def _serial_read(self, size):
        buff = self._serial.read(size)
        if len(buff) == 0:
            raise Exception("Got serial read timeout")
        return buff

    def get_flash_programmer(self):
        return UartRecoveryFlashProgrammer(self)

    def get_emmc_programmer(self, sdio_instance, partition_number, ack, bit_mode, uart_baud_rate=115200):
        return UartRecoveryEmmcProgrammer(self, sdio_instance, partition_number, ack, bit_mode, uart_baud_rate)

    def choose_storage(self):
        opcode = self.CHOOSE_STORAGE_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)

    def init_flash(self):
        opcode = self.WORK_WITH_FLASH_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)

    def init_emmc(self, sdio_instance, partition_number, ack, bit_mode):
        opcode = self.WORK_WITH_EMMC_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)

        sdio_instance_bin = sdio_instance.to_bytes(1, byteorder='little')
        self._serial.write(sdio_instance_bin)

        partition_number_bin = partition_number.to_bytes(1, byteorder='little')
        self._serial.write(partition_number_bin)

        ack_bin = ack.to_bytes(1, byteorder='little')
        self._serial.write(ack_bin)

        bit_mode_bin = bit_mode.to_bytes(1, byteorder='little')
        self._serial.write(bit_mode_bin)

    def get_fw_version(self):
        opcode = self.FW_VERSION_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)
        firmware_major = int.from_bytes(self._serial_read(4), "big")
        firmware_minor = int.from_bytes(self._serial_read(4), "big")
        return firmware_major, firmware_minor

    def get_jedec_id(self):
        opcode = self.JEDEC_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)
        return self._serial_read(self.JEDEC_ID_LENGTH).hex()

    def write(self, address, buffer_data):
        opcode = self.WRITE_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        address_bin = address.to_bytes(4, byteorder='little')
        length_bin = (len(buffer_data)).to_bytes(4, byteorder='little')
        self._serial.write(opcode_bin)
        self._serial.write(address_bin)
        self._serial.write(length_bin)
        self._serial.write(bytearray(buffer_data))
        end_ack = self._serial_read(1)
        assert end_ack == self.WRITE_END_ACK.to_bytes(1, byteorder='little'), "write didn't succeeded"

    def erase(self, address):
        opcode = self.ERASE_SECTOR_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        address_bin = address.to_bytes(4, byteorder='little')
        self._serial.write(opcode_bin)
        self._serial.write(address_bin)
        end_ack = self._serial_read(1)
        assert end_ack == self.ERASE_SECTOR_END_ACK.to_bytes(1, byteorder='little'), "Sector erase didn't succeeded"

    def read(self, address, length):
        read_data_buffer = bytearray([])
        opcode = self.READ_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        address_bin = address.to_bytes(4, byteorder='little')
        length_bin = length.to_bytes(4, byteorder='little')
        self._serial.write(opcode_bin)
        self._serial.write(address_bin)
        self._serial.write(length_bin)
        while (len(read_data_buffer) < length):
            read_data_buffer = read_data_buffer + self._serial_read(length - len(read_data_buffer))
        return bytearray(read_data_buffer)

    def jump_bootrom(self):
        opcode = self.JUMP_BOOTROM_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)

    def verify_fw_version(self):
        try:
            firmware_major, firmware_minor = self.get_fw_version()
        except Exception:
            raise Exception("Failed to load the recovery firmware, could not connect to the recovery agent. "
                            "Please try the following:\n"
                            "\t1. Make sure board is turned on.\n"
                            "\t2. Make sure bootstrap set to boot from uart.\n"
                            "\t3. The USB cable connected correctly\n"
                            "\t4. Reset the target and try again\n")

        if (firmware_major != FIRMWARE_VERSION_MAJOR) or (firmware_minor != FIRMWARE_VERSION_MINOR):
            raise Exception("Incompatibility between the loaded UART recovery firmware version "
                            f"({firmware_major}.{firmware_minor}) "
                            f"and the script version ({FIRMWARE_VERSION_MAJOR}.{FIRMWARE_VERSION_MINOR})")

        logger.info(
            f'UART recovery load firmware and script version: {firmware_major}.{firmware_minor}'
        )

    def set_baudrate(self, baudrate):
        opcode = self.SET_BAUDRATE_OPCODE
        opcode_bin = opcode.to_bytes(1, byteorder='little')
        baudrate_bin = baudrates_dictionary[baudrate].to_bytes(1, byteorder='little')
        self._serial.write(opcode_bin)
        self._serial.write(baudrate_bin)
        self._serial.close()
        self.UART_BAUDRATE = baudrate
        self.open_serial()
        time.sleep(0.5)


class UartRecoveryFlashProgrammer(StorageProgrammer):
    QSPI_SECTOR_SIZE = (4*1024)

    def __init__(self, comm: UartRecoveryCommunicator):
        self.comm = comm

    def init_flow(self):
        self.comm.choose_storage()
        self.comm.init_flash()

    def identify(self):
        self.comm.verify_fw_version()
        jedec_id = self.comm.get_jedec_id()
        jedec_id = ''.join('{:02x}'.format(x) for x in bytearray.fromhex(jedec_id)[::-1])

        logger.info(
            f'flash detected, flash jedec_id: 0x{jedec_id}'
        )

    def write(self, address, buffer_data):
        self.comm.write(address, buffer_data)

    def erase(self, address, length):
        for sector_offset in range(0, length, self.QSPI_SECTOR_SIZE):
            self.comm.erase(address + sector_offset)

    def read(self, address, length):
        read_data_buffer = bytearray()
        for read_offset in range(0, length, self.QSPI_SECTOR_SIZE):
            if read_offset + self.QSPI_SECTOR_SIZE > length:
                bytes_to_read = length - read_offset
            else:
                bytes_to_read = self.QSPI_SECTOR_SIZE
            read_data_buffer += self.comm.read(address + read_offset, bytes_to_read)
        return read_data_buffer

    def open_interface(self):
        self.comm.open_serial()
        self.init_flow()


class UartRecoveryEmmcProgrammer(StorageProgrammer):

    def __init__(self, comm: UartRecoveryCommunicator, sdio_instance, partition_number, ack, bit_mode,
                 uart_baud_rate=115200):
        self.comm = comm
        self.sdio_instance = sdio_instance
        self.partition_number = partition_number
        self.ack = ack
        self.bit_mode = bit_mode
        self.buff_size = 128 * EMMC_BLOCK_SIZE
        self.uart_baud_rate = uart_baud_rate

    def init_flow(self):
        self.comm.choose_storage()
        self.comm.init_emmc(self.sdio_instance, self.partition_number, self.ack, self.bit_mode)
        if (self.uart_baud_rate != self.comm.UART_BAUDRATE):
            self.comm.set_baudrate(self.uart_baud_rate)

    def identify(self):
        self.comm.verify_fw_version()

    def write(self, address, buffer_data):
        for i in range(0, len(buffer_data), self.buff_size):
            self.comm.write(address + i, buffer_data[i:i + self.buff_size])

    def erase(self, address, length):
        # no need to erase in emmc
        return

    def read(self, address, length):
        return self.comm.read(address, length)

    def open_interface(self):
        self.comm.open_serial()
        self.init_flow()
