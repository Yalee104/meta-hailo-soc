DESCRIPTION = "Install the SW user example for running the hailo-linux-init script"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING.MIT;md5=aa7321c8e0df442b97243c2e1d64c9ee"
TARGETDIR = "/etc"
SCRIPT_FILE_NAME = "hailo_linux_init.sh"
RDEPENDS:${PN} += "bash"

SRC_URI = "file://${SCRIPT_FILE_NAME} \
            file://COPYING.MIT"

S = "${WORKDIR}"

INITSCRIPT_NAME = "${SCRIPT_FILE_NAME}"
INITSCRIPT_PARAMS = "start 50 5 ."

inherit update-rc.d

do_install() {
    install -d ${D}${TARGETDIR}/init.d
    install -m 0755 ${WORKDIR}/${SCRIPT_FILE_NAME} ${D}${TARGETDIR}/init.d/${SCRIPT_FILE_NAME}
}



