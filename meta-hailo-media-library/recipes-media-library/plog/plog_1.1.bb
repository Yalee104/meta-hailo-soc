DESCRIPTION = "Plog is a portable, simple and extensible C++ logging library"
HOMEPAGE = "https://github.com/SergiusTheBest/plog"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=5e2a1e7f8253c4d42c1d8cd06eafdeed"

SRC_URI = "git://github.com/SergiusTheBest/plog.git;branch=master;protocol=https;rev=e21baecd4753f14da64ede979c5a19302618b752"
SRCREV = "e21baecd4753f14da64ede979c5a19302618b752"

S = "${WORKDIR}/git"

inherit allarch

do_install() {
    install -d ${D}${includedir}/plog
    cp -r ${S}/include/plog/* ${D}${includedir}/plog/
}

FILES:${PN} += "${includedir}/plog"

BBCLASSEXTEND = "native nativesdk"
