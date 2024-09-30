#!/usr/bin/env python

"""
The purpose of this application is to program the Hailo-15 board's flash with the relevant software and configurations.
"""

import argparse
import hashlib
import os
import time

from hailo15_board_tools.storage_programmers.storage_programmer import StorageProgrammer, logger
from hailo15_board_tools.storage_programmers.storage_manager import (StorageManager, validate_mac_address,
                                                                     StorageDataValidationException)
from hailo15_board_tools.storage_programmers.uart_recovery_manager import UartRecoveryCommunicator
from hailo15_board_tools.storage_programmers.ftdi_flash_programmer import FtdiFlashProgrammer


class Hailo15FlashManager(StorageManager):

    def __init__(self, programmer: StorageProgrammer, is_b_image: bool = False):
        self.programmer = programmer
        self.ab_offset = (self.STORAGE_B_IMAGE_OFFSET - self.STORAGE_A_IMAGE_OFFSET) if is_b_image else 0

    def program_storage(self, file_path, offset, reserved_section_size, validate, add_md5=False):
        if offset >= self.STORAGE_A_IMAGE_OFFSET:
            offset += self.ab_offset

        raw_section_size = os.path.getsize(file_path)
        if add_md5:
            raw_section_size += hashlib.md5().digest_size

        if reserved_section_size < raw_section_size:
            raise StorageDataValidationException("Provided file is larger than expected")

        logger.info(f"Erasing flash from {hex(offset)} B to {hex(offset + raw_section_size)} B...")
        # Erase function validates that offset and section size are inbounds of flash device
        self.programmer.erase(offset, raw_section_size)
        logger.info("Erased successfully")
        time.sleep(1)
        self._program_file(file_path, offset, raw_section_size, validate=validate, add_md5=add_md5)
        logger.info(f"Provided file {file_path} was successfully programmed")

    def erase_uboot_env_from_flash(self):
        logger.info("Erasing U-Boot env...")
        # Erase function validates that offset and section size are inbounds of flash device
        self.programmer.erase(self.STORAGE_OFFSET_UBOOT_ENV, self.STORAGE_SECTION_SIZE_UBOOT_ENV)
        time.sleep(1)


def run(scu_firmware=None, scu_bootloader=None, scu_bootloader_config=None, bootloader=None, bootloader_env=None,
        uboot_device_tree=None, customer_cert=None, uboot_tfa=None, verify=True, uart_load=False,
        serial_device_name='/dev/ttyUSB3', jump_to_flash=False, is_b_image=False, flash_mac_addr=None):
    if uart_load:
        uart_comm = UartRecoveryCommunicator(serial_device_name)
        programmer = uart_comm.get_flash_programmer()
    else:
        programmer = FtdiFlashProgrammer()

    flash_manager = Hailo15FlashManager(programmer, is_b_image)

    flash_manager.programmer.open_interface()
    flash_manager.programmer.identify()

    if scu_firmware:
        flash_manager.program_scu_fw(scu_firmware, validate=verify)
    if scu_bootloader:
        flash_manager.program_scu_bl(scu_bootloader, validate=verify)
    if scu_bootloader_config:
        flash_manager.program_scu_bl_config(scu_bootloader_config, validate=verify)
    if bootloader:
        flash_manager.program_uboot_spl(bootloader, validate=verify)
    # U-Boot env program must follow the uboot program
    if bootloader_env:
        flash_manager.program_uboot_env(bootloader_env, validate=verify)
    if customer_cert:
        flash_manager.program_customer_certificate(customer_cert, validate=verify)
    if uboot_device_tree:
        flash_manager.program_uboot_device_tree(uboot_device_tree, validate=verify)
    if flash_mac_addr:
        flash_manager.program_device_mac_config(flash_mac_addr, validate=verify)
    if uboot_tfa:
        flash_manager.program_uboot_tfa(uboot_tfa, validate=verify)

    if uart_load and jump_to_flash:
        uart_comm.jump_bootrom()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--scu-firmware',
        help='The path to the file containing the SCU firmware binary.')

    parser.add_argument(
        '--scu-bootloader',
        help='The path to the file containing the SCU bootloader binary.')

    parser.add_argument(
        '--scu-bootloader-config',
        help='The path to the file containing the SCU bootloader config binary.')

    parser.add_argument(
        '--bootloader',
        help='The path to the file containing the U-Boot SPL binary.')

    parser.add_argument(
        '--bootloader-env',
        help='The path to the file containing the U-Boot env.')

    parser.add_argument(
        '--uboot-device-tree',
        help='The path to the file containing the u-boot device tree.')

    parser.add_argument(
        '--customer-certificate',
        help='The path to the file containing the customer certificate.')

    parser.add_argument(
        '--uboot-tfa',
        help='The path to the file containing the U-Boot & TF-A itb.')

    parser.add_argument('--verify', type=int, choices=[0, 1], default=1,
                        help='Verify the written data by reviewing and comparing to the written data (default is true)')

    parser.add_argument('--uart-load', action='store_true',
                        help='Use UART for programming the SPI flash (default is false).')

    parser.add_argument('--serial-device-name', default='/dev/ttyUSB3',
                        help='The serial device name (default is /dev/ttyUSB3).')

    parser.add_argument('--b-image', action='store_true', help='Program B image.')

    parser.add_argument('--flash-mac-addr', type=validate_mac_address, default=None,
                        help='Set Flash Mac address, Mac format xx:xx:xx:xx:xx:xx')

    args = parser.parse_args()

    run(args.scu_firmware, args.scu_bootloader, args.scu_bootloader_config, args.bootloader, args.bootloader_env,
        args.uboot_device_tree, args.customer_certificate, args.uboot_tfa,  args.verify, args.uart_load,
        args.serial_device_name, args.b_image, flash_mac_addr=args.flash_mac_addr)


if __name__ == '__main__':
    main()
