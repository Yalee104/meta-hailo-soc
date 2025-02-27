DESCRIPTION = "U-Boot & TrustedFirmware-A image"

PACKAGE_ARCH = "${MACHINE_ARCH}"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://../COPYING.MIT;md5=aa7321c8e0df442b97243c2e1d64c9ee"
inherit deploy hailo-cc312-sign
SRC_URI = "file://u-boot-tfa.its \
	   file://COPYING.MIT"

HAILO_CC312_SIGNED_BINARY = "${B}/u-boot-spl.bin"
HAILO_CC312_UNSIGNED_BINARY = "${STAGING_DATADIR}/u-boot-spl-nodtb.bin"

DEPENDS += " dtc-native u-boot-tools-native u-boot"
do_compile[depends] += " u-boot:do_deploy trusted-firmware-a-hailo:do_deploy hailo-secureboot-assets:do_deploy"

do_compile() {
    ln -sf ${DEPLOY_DIR_IMAGE}/u-boot-nodtb.bin ${WORKDIR}/u-boot-nodtb.bin
    ln -sf ${DEPLOY_DIR_IMAGE}/bl31.bin ${WORKDIR}/bl31.bin
    uboot-mkimage -f ${WORKDIR}/u-boot-tfa.its ${B}/u-boot-tfa.itb
    # sign u-boot-tfa with customer key
    uboot-mkimage -F -k ${SPL_SIGN_KEYDIR} -r ${B}/u-boot-tfa.itb
    # sign u-boot-spl-nodtb.bin, generate u-boot-spl.bin
    do_hailo_cc312_sign
}

do_deploy() {
    install -m 0644 ${B}/u-boot-spl.bin ${B}/u-boot-tfa.itb ${DEPLOYDIR}/
    install -m 0644 ${WORKDIR}/u-boot-tfa.its ${DEPLOYDIR}/
}

addtask deploy after do_compile
