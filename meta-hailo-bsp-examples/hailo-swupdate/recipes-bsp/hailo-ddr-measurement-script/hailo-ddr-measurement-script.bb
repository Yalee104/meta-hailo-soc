DESCRIPTION = "Configure and run DDR measurement"
SECTION = "apps"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://../COPYING.MIT;md5=f734c2876134d7428e1917e1ede9f809"
RDEPENDS:${PN} += "bash"
targetdir = "/etc"

SRC_URI = "file://hailo_ddr_perf.sh \
           file://COPYING.MIT"

do_install() {
    install -m 0755 -d ${D}${targetdir}
    install -m 0500 ${WORKDIR}/hailo_ddr_perf.sh ${D}${targetdir}
}

FILES:${PN} += "${targetdir}/hailo_ddr_perf.sh"
