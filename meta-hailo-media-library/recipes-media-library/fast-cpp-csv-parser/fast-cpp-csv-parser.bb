SUMMARY = "A small, easy-to-use and fast header-only library for reading comma separated value (CSV) files."

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=d59bbf1a05590beb35b4b4b2c8458b70"

SRC_URI = "git://github.com/ben-strasser/fast-cpp-csv-parser.git;protocol=https;branch=master"

SRCREV = "a71a87e700b0fb92645c6b124742cbf326e0f7b1"

S = "${WORKDIR}/git"

# fast-cpp-csv-parser is a header-only C++ library, so the main package will be empty.
ALLOW_EMPTY:${PN} = "1"
ALLOW_EMPTY:${PN}-dev = "1"

do_install(){
    install -d ${D}${includedir}
    install -m 0644 ${S}/*.h ${D}${includedir}/
}

FILES:${PN} += "${includedir}/*.h"
FILES:${PN}-dev += "${includedir}/*.h"
