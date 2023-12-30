require recipes-bsp/trusted-firmware-a/trusted-firmware-a.inc

BRANCH = "1.2.0"
SRCREV = "43c493eb59e3bd454ee0afb8b3f7870864598241"
SRC_URI := "git://git@github.com/hailo-ai/arm-trusted-firmware.git;protocol=https;branch=${BRANCH}"

LIC_FILES_CHKSUM += "file://docs/license.rst;md5=b2c740efedc159745b9b31f88ff03dde"
LICENSE = "BSD-3-Clause"

COMPATIBLE_MACHINE:hailo15 = ".*"
TFA_PLATFORM:hailo15 = "hailo15"
TFA_BUILD_TARGET = "bl31"
