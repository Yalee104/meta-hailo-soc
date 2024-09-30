#!/usr/bin/env python

"""
The purpose of this application is to program the Hailo-15 board's emc with the relevant software and configurations.
"""

import argparse
import hashlib
import os
from enum import Enum

from hailo15_board_tools.storage_programmers.storage_programmer import StorageProgrammer, logger
from hailo15_board_tools.storage_programmers.storage_manager import (StorageManager, validate_mac_address,
                                                                     StorageDataValidationException)
from hailo15_board_tools.storage_programmers.uart_recovery_manager import UartRecoveryCommunicator


class EmmcBitMode(Enum):
    EMMC1_BIT = 0
    EMMC4_BIT = 1
    EMMC8_BIT = 2


class Hailo15EMMCManager(StorageManager):

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

        self._program_file(file_path, offset, raw_section_size, validate=validate, add_md5=add_md5)
        logger.info(f"Provided file was successfully {file_path} programmed")


def run(inst, boot_partition_number, ack, bit_mode, scu_firmware=None, scu_bootloader=None,
        scu_bootloader_config=None, bootloader=None, bootloader_env=None, uboot_device_tree=None,
        customer_cert=None, uboot_tfa=None, verify=True, serial_device_name='/dev/ttyUSB3',
        jump_to_boot=False, is_b_image=False, emmc_mac_addr=None, uart_baud_rate=115200):

    uart_comm = UartRecoveryCommunicator(serial_device_name)
    programmer = uart_comm.get_emmc_programmer(inst, boot_partition_number, ack, bit_mode.value, uart_baud_rate)

    emmc_manager = Hailo15EMMCManager(programmer, is_b_image)

    emmc_manager.programmer.open_interface()
    emmc_manager.programmer.identify()

    if scu_firmware:
        emmc_manager.program_scu_fw(scu_firmware, validate=verify)
    if scu_bootloader:
        emmc_manager.program_scu_bl(scu_bootloader, validate=verify)
    if scu_bootloader_config:
        emmc_manager.program_scu_bl_config(scu_bootloader_config, validate=verify)
    if bootloader:
        emmc_manager.program_uboot_spl(bootloader, validate=verify)
    # U-Boot env program must follow the uboot program
    if bootloader_env:
        emmc_manager.program_uboot_env(bootloader_env, validate=verify)
    if customer_cert:
        emmc_manager.program_customer_certificate(customer_cert, validate=verify)
    if uboot_device_tree:
        emmc_manager.program_uboot_device_tree(uboot_device_tree, validate=verify)
    if emmc_mac_addr:
        emmc_manager.program_device_mac_config(emmc_mac_addr, validate=verify)
    if uboot_tfa:
        emmc_manager.program_uboot_tfa(uboot_tfa, validate=verify)

    if jump_to_boot:
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
        '--bootloader',
        help='The path to the file containing the U-Boot SPL binary.')

    parser.add_argument(
        '--scu-bootloader-config',
        help='The path to the file containing the SCU bootloader config binary.')

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

    parser.add_argument('--serial-device-name', default='/dev/ttyUSB3',
                        help='The serial device name (default is /dev/ttyUSB3).')

    parser.add_argument('--b-image', action='store_true', help='Program B image.')

    parser.add_argument('--emmc-mac-addr', type=validate_mac_address, default=None,
                        help='Set EMMC Mac address, Mac format xx:xx:xx:xx:xx:xx')
    parser.add_argument('--sdio-instance',
                        default=1,
                        choices=[0, 1],
                        help='Choose which device to recover')
    parser.add_argument('--boot-partition-number',
                        default=1,
                        choices=[0, 1],
                        help='Choose which boot partition to work with')
    parser.add_argument('--no-ack',
                        action='store_true',
                        help='Choose if boot flow use ack or not')
    parser.add_argument('--emmc-bit-mode',
                        default=4,
                        choices=[1, 4, 8],
                        help='Choose which bit mode to work with')
    parser.add_argument('--uart-baud-rate',
                        type=int,
                        default=115200,
                        choices=[57600, 115200, 230400, 460800, 576000, 921600],
                        help='Choose baud rate to work with (relevant only for emmc)')

    args = parser.parse_args()

    # configure bit mode
    if (args.bit_mode == 1):
        bit_mode = EmmcBitMode.EMMC1_BIT
    if (args.bit_mode == 4):
        bit_mode = EmmcBitMode.EMMC4_BIT
    if (args.bit_mode == 8):
        bit_mode = EmmcBitMode.EMMC8_BIT

    run(args.sdio_instance, args.boot_partition_number, 0 if args.no_ack else 1, bit_mode,
        args.scu_firmware, args.scu_bootloader, args.scu_bootloader_config, args.bootloader, args.bootloader_env,
        args.uboot_device_tree, args.customer_certificate, args.uboot_tfa,  args.verify, args.serial_device_name,
        args.b_image, emmc_mac_addr=args.emmc_mac_addr, uart_baud_rate=args.uart_baud_rate)


if __name__ == '__main__':
    main()
