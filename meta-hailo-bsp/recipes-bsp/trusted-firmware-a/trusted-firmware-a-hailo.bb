require recipes-bsp/trusted-firmware-a/trusted-firmware-a.inc

BRANCH = "1.3.1"
SRCREV = "eb076520d78668be18edc44e131a578e2c0002cf"
SRC_URI := "git://git@github.com/hailo-ai/arm-trusted-firmware.git;protocol=https;branch=${BRANCH}"

LIC_FILES_CHKSUM += "file://docs/license.rst;md5=b2c740efedc159745b9b31f88ff03dde"
LICENSE = "BSD-3-Clause"

COMPATIBLE_MACHINE:hailo15 = ".*"
TFA_PLATFORM:hailo15 = "hailo15"
TFA_PLATFORM:hailo15l = "hailo15l"
TFA_BUILD_TARGET = "bl31"
EXTRA_OEMAKE:append:hailo15l-oregano = " HAILO_FPGA=1"
