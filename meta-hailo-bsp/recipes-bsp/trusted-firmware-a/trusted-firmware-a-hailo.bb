require recipes-bsp/trusted-firmware-a/trusted-firmware-a.inc

BRANCH = "1.4.0"
SRCREV = "11dfe5ed76832f62bfb48c43e74e4a2a131576e5"
SRC_URI := "git://git@github.com/hailo-ai/arm-trusted-firmware.git;protocol=https;branch=${BRANCH}"

LIC_FILES_CHKSUM += "file://docs/license.rst;md5=b2c740efedc159745b9b31f88ff03dde"
LICENSE = "BSD-3-Clause"

COMPATIBLE_MACHINE:hailo15 = ".*"
TFA_PLATFORM:hailo15 = "hailo15"
TFA_PLATFORM:hailo15l = "hailo15l"
TFA_BUILD_TARGET = "bl31"
EXTRA_OEMAKE:append:hailo15l-oregano = " HAILO_FPGA=1"
