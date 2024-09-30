from pyftdi.spi import SpiController
from spiflash import serialflash
from spiflash.serialflash import _Gen25FlashDevice, SerialFlashManager
from pyftdi.misc import pretty_size
import math

from hailo15_board_tools.storage_programmers.storage_programmer import StorageProgrammer, logger

# Override with our device values
serialflash.N25QFlashDevice.DEVICES.clear()
serialflash.N25QFlashDevice.DEVICES = ({0xBA: 'Micron N25Q', 0xBB: 'Micron MT25'})
serialflash.N25QFlashDevice.SIZES.clear()
serialflash.N25QFlashDevice.SIZES = {0x15: 1 << 21, 0x16: 1 << 22, 0x17: 1 << 23, 0x18: 1 << 24, 0x21: 1 << 30}

serialflash.W25xFlashDevice.DEVICES.clear()
serialflash.W25xFlashDevice.DEVICES = {0x30: 'Winbond W25X', 0x40: 'Winbond W25Q', 0x60: 'Winbond W25Q'}
serialflash.W25xFlashDevice.SIZES.clear()
serialflash.W25xFlashDevice.SIZES = {0x11: 1 << 17, 0x12: 1 << 18, 0x13: 1 << 19, 0x14: 1 << 20,
                                     0x15: 2 << 20, 0x17: 8 << 20, 0x18: 16 << 20, 0x16: 32 << 20, 0x19: 256 << 20}

serialflash.Mx25lFlashDevice.DEVICES.clear()
serialflash.Mx25lFlashDevice.DEVICES = {0x9E: 'Macronix MX25D',
                                        0x26: 'Macronix MX25E',
                                        0x20: 'Macronix MX25E06',
                                        0x25: 'Macronix MX25U'}
serialflash.Mx25lFlashDevice.SIZES.clear()
serialflash.Mx25lFlashDevice.SIZES = {0x15: 2 << 20, 0x16: 4 << 20, 0x17: 8 << 20, 0x18: 16 << 20, 0x36: 32 << 20}

# ISSI flash


class ISS25xFlashDevice(_Gen25FlashDevice):
    """ISSI 25W/25L flash device implementation"""

    JEDEC_ID = 0x9D
    DEVICES = {0x60: 'IS25L', 0x70: 'IS25W'}
    SIZES = {0x11: 1 << 17, 0x12: 1 << 18, 0x13: 1 << 19, 0x14: 1 << 20, 0x15: 2 << 20,
             0x16: 4 << 20, 0x17: 8 << 20, 0x18: 16 << 20, 0x19: 32 << 20}
    SPI_FREQ_MAX = 104  # MHz
    CMD_READ_UID = 0x4B
    UID_LEN = 0x8  # 64 bits
    READ_UID_WIDTH = 4  # 4 dummy bytes
    TIMINGS = {'page': (0.0015, 0.003),  # 1.5/3 ms
               'subsector': (0.200, 0.200),  # 200/200 m
               'sector': (1.0, 1.0),  # 1/1 s
               'bulk': (32, 64),  # seconds
               'lock': (0.05, 0.1),  # 50/100 ms
               'chip': (4, 11)}
    FEATURES = (serialflash.SerialFlash.FEAT_SECTERASE |
                serialflash.SerialFlash.FEAT_SUBSECTERASE |
                serialflash.SerialFlash.FEAT_CHIPERASE)

    def __init__(self, spi, jedec):
        super(ISS25xFlashDevice, self).__init__(spi)
        if not ISS25xFlashDevice.match(jedec):
            raise serialflash.SerialFlashUnknownJedec(jedec)
        device, capacity = jedec[1:3]
        self._device = self.DEVICES[device]
        self._size = ISS25xFlashDevice.SIZES[capacity]

    def __str__(self):
        return 'ISSI %s%d %s' % \
            (self._device, len(self) >> 17,
             pretty_size(self._size, lim_m=1 << 20))

# Register the ISSI flash device (add it to the serialflash module)


serialflash.ISSI25xFlashDevice = ISS25xFlashDevice


class FtdiFlashProgrammer(StorageProgrammer):

    FTDI_INTERFACE = 2
    FTDI_URL = f'ftdi://ftdi:4232h/{FTDI_INTERFACE}'

    def __init__(self, url=FTDI_URL, freq=30E6):
        self.url = url
        self.freq = freq
        self.spi_controller = None

    def open_interface(self):
        self.spi_controller = SpiController()
        self.spi_controller.configure(self.url)

    def write(self, address, buffer_data):
        return self._flash_device.write(address, buffer_data)

    def read(self, address, length):
        return self._flash_device.read(address, length)

    def erase(self, address, length):
        subsector_size = self._flash_device.get_size('subsector')
        block_amount = math.ceil(length / subsector_size)
        section_size = block_amount * subsector_size
        return self._flash_device.erase(address, section_size)

    def identify(self):
        self._flash_device = SerialFlashManager().get_from_controller(self.spi_controller, cs=0, freq=self.freq)
        logger.info(f'flash detected "{self._flash_device}"')

    def close(self):
        if self.spi_controller:
            self.spi_controller.terminate()
            self.spi_controller = None
            logger.info("Close flash interface")
