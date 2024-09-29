LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://../COPYING.MIT;md5=aa7321c8e0df442b97243c2e1d64c9ee"
SRC_URI = " \
    file://hailo15_boot_image_sign.sh \
    file://hailo15_scu_image_sign.sh \
    file://hailo15_customer_key_sign.sh \
    file://prepare_scu_firmware_certificate_chain.py \
    file://hailo15_customer_certificate_generate.sh \
    file://hailo15_content_certificate_config_template.txt \
    file://hailo15_images_table_template.txt \
    file://hailo15_key_certificate_config_template.txt \
    file://COPYING.MIT \
    "
RDEPENDS:${PN} = "cryptocell-312-runtime-native"
# for envsubst command
RDEPENDS:${PN} += "gettext-runtime-native"
RDEPENDS:${PN} += "openssl-native"

inherit native

do_install () {
    install -d ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_boot_image_sign.sh ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_scu_image_sign.sh ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_customer_key_sign.sh ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/prepare_scu_firmware_certificate_chain.py ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_customer_certificate_generate.sh ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_content_certificate_config_template.txt ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_images_table_template.txt ${D}${bindir}
    install -m 0755 -D ${WORKDIR}/hailo15_key_certificate_config_template.txt ${D}${bindir}
}
