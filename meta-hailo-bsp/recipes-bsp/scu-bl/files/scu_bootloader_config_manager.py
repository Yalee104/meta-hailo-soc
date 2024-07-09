#!/usr/bin/env python3

"""
The purpose of this utility is to parse SCU bootloader configuration JSON file and create a bin file with this config
"""
import argparse
import json
import binascii
import os
import struct
import ctypes
from enum import Enum

SCU_BL_MAX_IMAGES = 4
SCU_BL_IMAGE_SOURCE_MAX = 6


class Scu_bl_boot_image_source(Enum):
    BOOT_IMAGE_SOURCE_BOOTSTRAP = ("bootstrap", 0)
    BOOT_IMAGE_SOURCE_SPI_FLASH = ("spi_flash", 1)
    BOOT_IMAGE_SOURCE_UART = ("uart", 2)
    BOOT_IMAGE_SOURCE_PCIE = ("pcie", 3)
    BOOT_IMAGE_SOURCE_EMMC0 = ("emmc0", 4)
    BOOT_IMAGE_SOURCE_EMMC1 = ("emmc1", 5)


class Scu_bl_boot_image_mode(Enum):
    BOOT_IMAGE_MODE_NORMAL = ("normal", 0)
    BOOT_IMAGE_MODE_REMOTE_UPDATE = ("remote_update", 1)

  
class Image_descriptor_C_struct(ctypes.Structure):
    _fields_ = [
        ("boot_image_offset", ctypes.c_uint32),
        ("boot_image_source", ctypes.c_uint8),
        ("boot_image_mode", ctypes.c_uint8)
    ]


class Scu_bl_config_C_struct(ctypes.Structure):
    _fields_ = [
        ("crc_val", ctypes.c_uint32),
        ("actual_config_size_bytes", ctypes.c_uint16),
        ("boot_max_retries", ctypes.c_uint8),
        ("image_descriptors", Image_descriptor_C_struct * SCU_BL_MAX_IMAGES),
        ("last_valid_desc_index", ctypes.c_uint8),
        ("debug_logs_enabled", ctypes.c_uint8)
    ]

    def __init__(self, crc_val, actual_config_size_bytes, boot_max_retries,
                image_descriptors, last_valid_desc_index, debug_logs_enabled):
        self.crc_val = crc_val
        self.actual_config_size_bytes = actual_config_size_bytes
        self.boot_max_retries = boot_max_retries

        for i in range(SCU_BL_MAX_IMAGES):
            self.image_descriptors[i].boot_image_offset = image_descriptors[i].boot_image_offset
            self.image_descriptors[i].boot_image_source = image_descriptors[i].boot_image_source
            self.image_descriptors[i].boot_image_mode = image_descriptors[i].boot_image_mode

        self.last_valid_desc_index = last_valid_desc_index
        self.debug_logs_enabled = debug_logs_enabled


def parse_and_validate_image_descriptors(json_content):
    image_descriptors = []

    for d in json_content['image_descriptors']:
        boot_image_offset_str = d['boot_image_offset']
        boot_image_source_str = d['boot_image_source']
        boot_image_mode_str = d['boot_image_mode']

        boot_image_offset = int(boot_image_offset_str, 16)

        if not isinstance(boot_image_offset, int) or (boot_image_offset < 0) or (boot_image_offset >= 2**32):
            raise ValueError("Invalid value for boot_image_offset")
        
        # Get the integer value of boot_image_source
        boot_image_source = next((source.value[1] for source in Scu_bl_boot_image_source if source.value[0] == boot_image_source_str), None)
        if boot_image_source is None:
            raise ValueError(f"Invalid value for boot_image_source: {boot_image_source_str}")

        # Get the integer value of boot_image_mode
        boot_image_mode = next((mode.value[1] for mode in Scu_bl_boot_image_mode if mode.value[0] == boot_image_mode_str), None)
        if boot_image_mode is None:
            raise ValueError(f"Invalid value for boot_image_mode: {boot_image_mode_str}")

        image_descriptor = Image_descriptor_C_struct(int(boot_image_offset_str, 16), boot_image_source, boot_image_mode)
        image_descriptors.append(image_descriptor)  

    # Ensure that the number of image descriptors is correct
    if len(image_descriptors) != SCU_BL_MAX_IMAGES:
        raise ValueError("Invalid number of image descriptors")

    return image_descriptors  


# Validate values of additional parameters in JSON file
def validate_additional_parameters(boot_max_retries, last_valid_desc_index, debug_logs_enabled):
    if not isinstance(boot_max_retries, int) or boot_max_retries > 0xFF or boot_max_retries < 0:
        raise ValueError("Invalid value for boot_max_retries")
    if not isinstance(last_valid_desc_index, int) or \
        (last_valid_desc_index >= SCU_BL_MAX_IMAGES) or \
            (last_valid_desc_index < 0):
        raise ValueError("Invalid value for last_valid_desc_index")
    if not isinstance(debug_logs_enabled, bool):
            raise ValueError("Invalid value for debug_logs_enabled")
    

def load_config_from_json(file_path):
    if (ctypes.sizeof(Scu_bl_config_C_struct) % 4) != 0:
        raise ValueError(f"Invalid size of SCU BL config structure: {ctypes.sizeof(Scu_bl_config_C_struct)} - not a multiple of 4 bytes")

    with open(file_path, 'r') as file:
        json_content = json.load(file)

        # Parse and validatate image descriptors
        image_descriptors = parse_and_validate_image_descriptors(json_content)

        # Parse & validate the additional parameters
        boot_max_retries = int(json_content.get('boot_max_retries'),16)
        last_valid_desc_index = json_content.get('last_valid_desc_index')
        debug_logs_enabled = json_content.get('debug_logs_enabled')

        validate_additional_parameters(boot_max_retries, last_valid_desc_index, debug_logs_enabled)

        actual_config_size_bytes = ctypes.sizeof(Scu_bl_config_C_struct)

        # Create a new instance of Scu_bl_config_C_struct
        scu_bl_config_C_struct = Scu_bl_config_C_struct(
            crc_val=0,
            actual_config_size_bytes=actual_config_size_bytes,
            boot_max_retries=boot_max_retries,
            image_descriptors=image_descriptors,
            last_valid_desc_index=last_valid_desc_index,
            debug_logs_enabled=debug_logs_enabled
        )        
    return scu_bl_config_C_struct


def create_scu_bl_config_bin_file(jsonFileName, binFile):
    scu_bl_config_c_struct = load_config_from_json(jsonFileName)

    binary_data = ctypes.string_at(ctypes.addressof(scu_bl_config_c_struct) + ctypes.sizeof(ctypes.c_uint32), 
                                     ctypes.sizeof(scu_bl_config_c_struct) - ctypes.sizeof(ctypes.c_uint32))

    # number of 32bit words in scu_bl_config - excluding the CRC field
    words_num = len(binary_data) // 4

    # Swap endianness of the binary data
    reversed_binary_data = struct.pack('>' + ('I' * words_num), *(struct.unpack(('I' * words_num), binary_data)))

    # bit reverse the binary data
    bit_reversed_data = bytes([int('{:08b}'.format(byte)[::-1], 2) for byte in reversed_binary_data])

    # CRC generation
    # Library function binascii.crc32 is using CRC-32 algorithm with bit-reversed
    # input and bit-reversed & FF-XORed output CRC
    # The CRC module on SoC is working with CRC-32-MPEG-2, in which the is no bit reversal
    # Therefore - performing relevant bit manipulations
    calculated_crc = binascii.crc32(bit_reversed_data)

    # bit reverse the calculated CRC and XOR it with 0xFFFFFFFF
    bit_reversed_XORed_calculated_crc = int('{:032b}'.format(calculated_crc)[::-1], 2) ^ 0xFFFFFFFF

    binFile.write(struct.pack('<I', bit_reversed_XORed_calculated_crc))
    binFile.write(binary_data)
    binFile.flush()

def run(scu_bl_cfg_json_path, scu_bl_cfg_bin_path=None):
    # if path to SCU BL config binary file is provided - create it now
    if scu_bl_cfg_bin_path:
        with open(scu_bl_cfg_bin_path, 'wb') as scu_bl_cfg_bin:
            create_scu_bl_config_bin_file(scu_bl_cfg_json_path, scu_bl_cfg_bin)
            scu_bl_cfg_bin.flush()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--scu-bl-cfg-json',
        help='The path to json file to parse - containing SCU bootloader configuration.')
    
    parser.add_argument(
        '--scu-bl-cfg-bin',
        help='The path to bin file to create.')

    args = parser.parse_args()

    run(args.scu_bl_cfg_json, args.scu_bl_cfg_bin)

if __name__ == '__main__':
    main()