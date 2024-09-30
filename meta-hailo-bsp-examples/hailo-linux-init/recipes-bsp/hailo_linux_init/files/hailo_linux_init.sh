#!/bin/sh

# If an argument is provided, write it to boot_success_ap_software, otherwise write 1
if [ -n "$1" ] && [[ "$1" =~ ^[0-9]+$ ]] 2>/dev/null; then
    echo "$1" > /sys/devices/soc0/boot_info/boot_success_ap_software
else
    echo 1 > /sys/devices/soc0/boot_info/boot_success_ap_software
fi

exec 2> /dev/console