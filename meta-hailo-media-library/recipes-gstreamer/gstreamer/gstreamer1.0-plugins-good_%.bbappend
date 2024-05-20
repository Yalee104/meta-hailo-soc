FILESEXTRAPATHS:prepend:hailo15 := "${THISDIR}/files/:"

SRC_URI:append:hailo15 = "file://hailo_v4l2_meta.patch;striplevel=3;md5=2d36f2c23cb2600d2419a8b8b21e5b1b"

do_install:append(){
    install -d ${D}${includedir}/
    install -d ${D}${includedir}/hailo_v4l2/

    install -m 0644 ${S}/sys/v4l2/hailo_v4l2/*.h ${D}${includedir}/hailo_v4l2/
}

FILES:${PN}-dev += "${includedir}/hailo_v4l2 ${includedir}/hailo_v4l2/*"