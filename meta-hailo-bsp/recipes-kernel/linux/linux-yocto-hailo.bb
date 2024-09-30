DESCRIPTION = "Linux kernel"
SECTION = "kernel"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

inherit deploy hailo-cc312-sign

LINUX_VERSION = "5.15.32"
PV = "${LINUX_VERSION}"

LINUX_YOCTO_HAILO_URI ??= "git@github.com/hailo-ai/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH ??= "1.5.0"
LINUX_YOCTO_HAILO_SRCREV ??= "0baac6f43527cff8f4c92ed50c039c7b43bde722"
LINUX_YOCTO_HAILO_BOARD_VENDOR ?= "hailo"

KBRANCH = "${LINUX_YOCTO_HAILO_BRANCH}"
SRCREV = "${LINUX_YOCTO_HAILO_SRCREV}"

SIGNED_UBOOT_DTB = "${B}/${UBOOT_DTB_BINARY}.signed"

SRC_URI = "git://${LINUX_YOCTO_HAILO_URI};protocol=https;branch=${KBRANCH} \
           file://defconfig \
           file://cfg/;destsuffix=cfg;type=kmeta"
SRC_URI:append = "${@bb.utils.contains('MACHINE_FEATURES', 'kernel_debug_en', ' file://cfg/debug-configuration.cfg', '', d)}"
SRC_URI:append = "${@bb.utils.contains('MACHINE_FEATURES', 'dma_zone_disable', ' file://cfg/dma-zone-disable.cfg', '', d)}"
SRC_URI:append:hailo10-m2 = " file://cfg/dma-zone-disable.cfg"

SDIO0_POSTFIX = "${@bb.utils.contains('MACHINE_FEATURES', 'sdio0', '-sdio0', '', d)}"
KERNEL_DEVICETREE ?= "${LINUX_YOCTO_HAILO_BOARD_VENDOR}/${MACHINE}${SDIO0_POSTFIX}.dtb"

KCONFIG_MODE="--alldefconfig"

# customer certificate is deployed by the hailo-secureboot-assets
# and used for signing the fitimage
do_assemble_fitimage[depends] += "hailo-secureboot-assets:do_deploy"

do_assemble_fitimage:append() {
    # sign u-boot.dtb, generate u-boot.dtb.signed
    hailo15_boot_image_sign ${B}/${UBOOT_DTB_BINARY} devicetree ${SIGNED_UBOOT_DTB}
}

kernel_do_deploy:append() {
    install -m 0644 ${SIGNED_UBOOT_DTB} ${DEPLOYDIR}/
}

require recipes-kernel/linux/linux-yocto.inc

RRECOMMENDS:${KERNEL_PACKAGE_NAME}-base = ""
