DESCRIPTION = "Set ulimit for file descriptors"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://../ulimit.sh;md5=0058525134add3a8d8845fb8365182fa"

SRC_URI = "file://ulimit.sh"


do_install() {
    install -d ${D}${sysconfdir}/profile.d
    install -m 0755 ${WORKDIR}/ulimit.sh ${D}${sysconfdir}/profile.d/
}

FILES_${PN} += "${sysconfdir}/profile.d/ulimit.sh"
