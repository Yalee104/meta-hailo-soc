SUMMARY = "Verisilicon vivante SW package user space code build"
LICENSE = "MIT & Proprietary-VSI"
LIC_FILES_CHKSUM = "file://${B}/LICENSE;md5=805d1be5d56ae9500316a754de03ab5f \
					file://${S}/LICENSE;md5=8349eaff29531f0a3c4f4c8b31185958"

INHERITS = "externalsrc ccache"
RDEPENDS_IMAGING_SUB_SYSTEM = ""
DEPENDS_IMAGING_SUB_SYSTEM = "libdrm"

inherit ${INHERITS}

RDEPENDS:${PN} += "${RDEPENDS_IMAGING_SUB_SYSTEM}"
DEPENDS += "${DEPENDS_IMAGING_SUB_SYSTEM}"

SRC_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.4.0/imaging-sub-system.tar.gz"
SRC_URI[sha256sum] = "223adabe068921e2220260ce7c0b3aedbde1e7aefe83f640247af5844ba9f3c3"

B = "${WORKDIR}/imaging-sub-system/build"
S = "${WORKDIR}/imaging-sub-system/scripts"

LIBS_FILES_TO_COPY ?= ""

copy_lib_files() {
    cp -R --no-dereference --preserve=mode,links -v ${B}/dist/lib/*${LIBS_FILES_TO_COPY} ${D}/lib
	cp -R --no-dereference --preserve=mode,links -v ${B}/dist/release/lib/*${LIBS_FILES_TO_COPY} ${D}/lib
}

copy_lib_files() {
    cp -R --no-dereference --preserve=mode,links -v ${B}/dist/lib/*${LIBS_FILES_TO_COPY} ${D}/lib
	cp -R --no-dereference --preserve=mode,links -v ${B}/dist/release/lib/*${LIBS_FILES_TO_COPY} ${D}/lib
}

install_isp_media_server() {

	install -m 0755 -D  ${B}/dist/release/bin/isp_media_server ${D}${bindir}

	install -m 0755 -D  ${S}/hailo_cfg/isp_media_server ${D}/etc/init.d
	ln -s -r ${D}/etc/init.d/isp_media_server ${D}/etc/rc5.d/S20isp_media_server
}

install_dist() {
	install -m 0644 -D  ${B}/dist/bin/sony_imx334.xml ${D}${bindir}
	install -m 0644 -D  ${B}/dist/bin/sony_imx675*.xml ${D}${bindir}
	install -m 0644 -D  ${B}/dist/bin/sony_imx678*.xml ${D}${bindir}
	install -m 0755 -D  ${B}/dist/bin/*.so ${D}${bindir}
	install -m 0755 -D  ${B}/dist/release/bin/*.json ${D}${bindir}
	install -m 0755 -D  ${B}/dist/release/bin/*.cfg ${D}${bindir}
}

link_drivers() {
	ln -s -r ${D}/lib/libHAILO_IMX334.so ${D}${bindir}/HAILO_IMX334.drv
	ln -s -r ${D}/lib/libHAILO_IMX675.so ${D}${bindir}/HAILO_IMX675.drv
	ln -s -r ${D}/lib/libHAILO_IMX678.so ${D}${bindir}/HAILO_IMX678.drv
	ln -s -r ${D}/lib/libHAILO_IMX678_HDR.so ${D}${bindir}/HAILO_IMX678_HDR.drv
}

do_install() {
	install -d ${D}/lib
	install -d ${D}/etc
	install -d ${D}/etc/init.d
	install -d ${D}/etc/rc5.d
	install -d ${D}${bindir}

    copy_lib_files
	install_isp_media_server
    install_dist

	install -m 0755 -D  ${S}/mediacontrol/server/media_server_cfg*.json ${D}${bindir}

	link_drivers
}

PACKAGES = "${PN} ${PN}-dev"
INSANE_SKIP:${PN}-dev =  "file-rpaths dev-so debug-files rpaths staticdev installed-vs-shipped"
INSANE_SKIP:${PN} =  "file-rpaths dev-so debug-files rpaths staticdev installed-vs-shipped"

# FIXME: why? arch? 
do_package_qa[noexec] = "1"
EXCLUDE_FROM_SHLIBS = "1"

FILES:${PN}     += "/lib/* /lib/*/*"
FILES:${PN}     += "${bindir}/*"
