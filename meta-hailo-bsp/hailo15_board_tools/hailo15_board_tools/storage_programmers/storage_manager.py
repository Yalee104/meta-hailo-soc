from abc import ABC, abstractmethod
import tempfile
from contextlib import contextmanager
import struct
import re
import subprocess
import argparse
import hashlib
from hailo15_board_tools.storage_programmers.storage_programmer import logger
import os


MAC_ADDR_FORMAT_LEN = 17


class StorageDataValidationException(Exception):
    pass


class StorageManager(ABC):

    STORAGE_OFFSET_SCU_BL = 0
    STORAGE_SECTION_SIZE_SCU_BL = 0x5000
    STORAGE_OFFSET_SCU_BL_CONFIG_1 = 0x5000
    STORAGE_OFFSET_SCU_BL_CONFIG_2 = 0x6000
    STORAGE_SECTION_SIZE_SCU_BL_CONFIG = 0x1000
    STORAGE_OFFSET_DEVICE_CONFIG = 0x7000
    STORAGE_SECTION_SIZE_DEVICE_CONFIG = 0x1000
    STORAGE_OFFSET_SCU_FW = 0x8000
    STORAGE_SECTION_SIZE_SCU_FW = 0x38000
    STORAGE_OFFSET_UBOOT_DEVICE_TREE = 0x40000
    STORAGE_SECTION_SIZE_UBOOT_DEVICE_TREE = 0xF000
    STORAGE_OFFSET_CUSTOMER_CERTIFICATE = 0x4F000
    STORAGE_SECTION_SIZE_CUSTOMER_CERTIFICATE = 0x1000
    STORAGE_OFFSET_SPL_UBOOT_BIN = 0x54000
    STORAGE_SECTION_SIZE_UBOOT_SPL = 0x2C000
    STORAGE_OFFSET_UBOOT_ENV = 0x50000
    STORAGE_SECTION_SIZE_UBOOT_ENV = 0x4000
    # if working with a/b - notice to change STORAGE_B_IMAGE_OFFSET as well
    STORAGE_OFFSET_UBOOT_TFA = 0x80000
    STORAGE_SECTION_SIZE_UBOOT_TFA = 0x100000  # 1024 KB

    STORAGE_B_IMAGE_OFFSET = 0x80000
    STORAGE_A_IMAGE_OFFSET = 0x8000

    def _program_file(self, file_path, offset, section_size, validate, add_md5=False):
        """ This function programs a given file to the storage

        Args:
            file_path (str): The file path to program to the storage
            offset (hex): The start offset in the storage
            section_size (hex): The section size of the given file
            validate (bool, optional): Whether to validate content has been programmed successfully . Defaults to True.
            add_md5 (bool, optional): Whether to add md5 to the end of the file. Defaults to False.

        Raises:
            StorageDataValidationException: raise if validation failed or the file is larger than the section size
        """
        data_to_write = None
        with open(file_path, 'rb') as input_file:
            data_to_write = input_file.read()

        if add_md5:
            md5 = hashlib.md5()
            md5.update(data_to_write)
            data_to_write = b''.join([data_to_write, md5.digest()])

        if section_size < len(data_to_write):
            raise StorageDataValidationException("Provided file is larger than expected")

        self.programmer.write(offset, data_to_write)

        if validate:
            read_data = self.programmer.read(offset, len(data_to_write))
            if read_data != data_to_write:
                raise StorageDataValidationException("Storage was not programmed successfully")
            else:
                logger.info('Storage program validatation passed successfully')

    @abstractmethod
    def program_storage(self, file_path, offset, reserved_section_size, validate, add_md5=False):
        pass

    def program_device_mac_config(self, storage_mac_addr, validate=1):
        logger.info("Programming Mac address {}".format(storage_mac_addr))
        with tempfile.NamedTemporaryFile(suffix=".bin") as mac_config:
            mac_bytes = bytes.fromhex(storage_mac_addr.replace(':', ''))
            mac_config.write(mac_bytes)
            mac_config.flush()
            self.program_storage(mac_config.name,
                                 offset=self.STORAGE_OFFSET_DEVICE_CONFIG,
                                 reserved_section_size=self.STORAGE_SECTION_SIZE_DEVICE_CONFIG, validate=validate)

    def program_scu_fw(self, file_path, validate=1):
        logger.info(f"Programming SCU firmware file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_SCU_FW,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_SCU_FW, validate=validate)

    def program_scu_bl_config(self, file_path, validate=1):
        logger.info("Programming SCU bootloader config file...")
        local_file_path = file_path

        # if SCU BL config does not exist, write the ab_offset value to config location for backward compatibility
        if not os.path.exists(file_path):
            logger.info(f"{file_path} doesn't exist, writing only offset to SCU BL config (backward compatibility)")
            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as scu_bl_config:
                scu_bl_config.write(struct.pack('<I', self.ab_offset))
                scu_bl_config.flush()

                local_file_path = scu_bl_config.name

        # Always program the SCU BL config file to both locations 0x5000 and 0x6000
        self.program_storage(local_file_path,
                             offset=self.STORAGE_OFFSET_SCU_BL_CONFIG_1,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_SCU_BL_CONFIG, validate=validate)
        self.program_storage(local_file_path,
                             offset=self.STORAGE_OFFSET_SCU_BL_CONFIG_2,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_SCU_BL_CONFIG, validate=validate)

    def program_scu_bl(self, file_path, validate=1):
        logger.info(f"Programming SCU bootloader file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_SCU_BL,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_SCU_BL, validate=validate)

    def program_uboot_spl(self, file_path, validate=1):
        logger.info(f"Programming U-Boot SPL file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_SPL_UBOOT_BIN,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_UBOOT_SPL, validate=validate)

    @contextmanager
    def create_uboot_env(self, env_path, env_size):
        env_image_path = tempfile.NamedTemporaryFile(suffix=".bin")
        try:
            subprocess.run(["mkenvimage", "-s", str(env_size), "-o", env_image_path.name, env_path])
            yield env_image_path
        finally:
            env_image_path.close()

    def program_uboot_env(self, file_path, validate=1):
        logger.info(f"Programming U-Boot env file: {file_path}...")
        with self.create_uboot_env(file_path, self.STORAGE_SECTION_SIZE_UBOOT_ENV) as env_image_path:
            logger.info(f"Programming U-Boot env file: {env_image_path.name}...")
            self.program_storage(env_image_path.name,
                                 offset=self.STORAGE_OFFSET_UBOOT_ENV,
                                 reserved_section_size=self.STORAGE_SECTION_SIZE_UBOOT_ENV, validate=validate)

    def program_uboot_device_tree(self, file_path, validate=1):
        logger.info(f"Programming u-boot device-tree file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_UBOOT_DEVICE_TREE,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_UBOOT_DEVICE_TREE, validate=validate)

    def program_customer_certificate(self, file_path, validate=1):
        logger.info(f"Programming Customer certificate file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_CUSTOMER_CERTIFICATE,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_CUSTOMER_CERTIFICATE,
                             validate=validate)

    def program_uboot_tfa(self, file_path, validate=1):
        logger.info(f"Programming U-Boot & TF-A file: {file_path}...")
        self.program_storage(file_path,
                             offset=self.STORAGE_OFFSET_UBOOT_TFA,
                             reserved_section_size=self.STORAGE_SECTION_SIZE_UBOOT_TFA,
                             validate=validate)


def validate_mac_address(mac_addr):
    if len(mac_addr) != MAC_ADDR_FORMAT_LEN:
        raise argparse.ArgumentTypeError(f"Invalid MAC address: {mac_addr}")
    if not re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac_addr):
        raise argparse.ArgumentTypeError(f"Invalid MAC address: {mac_addr}")
    return mac_addr
