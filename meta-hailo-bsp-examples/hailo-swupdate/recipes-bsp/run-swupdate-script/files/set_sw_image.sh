#!/bin/bash

set -e

function write_scu_bl_cfg_bin()
{
    scu_bl_cfg_filename=$1
    echo "writing scu_bl configuration file named '$scu_bl_cfg_filename'"

    # Write SCU bootloader configuration to flash at offset 0x5000
    dd if=${scu_bl_cfg_filename} of=/dev/mtdblock0 bs=4096 count=1 seek=5 2>/dev/null

    # Write the same SCU bootloader configuration also to flash at offset 0x6000
    dd if=${scu_bl_cfg_filename} of=/dev/mtdblock0 bs=4096 count=1 seek=6 2>/dev/null
}

function usage()
{
    echo "Set SW image used for next boot in SCU bootloader configuration in QSPI flash."
    echo "Usage: set_sw_image.sh [a/b/remote_update]"
    echo ""

    return 0
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

next_boot_copy=$1

if [[ ${next_boot_copy} != "a" && ${next_boot_copy} != "b" && ${next_boot_copy} != "remote_update" ]]; then
    usage
    exit 1
fi

if [ ${next_boot_copy} = "a" ]; then
    write_scu_bl_cfg_bin "/etc/scu_bl_cfg/scu_bl_cfg_a.bin"
fi

if [ ${next_boot_copy} = "b" ]; then
    write_scu_bl_cfg_bin "/etc/scu_bl_cfg/scu_bl_cfg_b.bin"
fi

if [ ${next_boot_copy} = "remote_update" ]; then
    write_scu_bl_cfg_bin "/etc/scu_bl_cfg/scu_bl_cfg_a_remote_update.bin"
fi
