DESCRIPTION = "Media Library vision control application \
               fetches the client application that allows control media library image properties"
LICENSE = "CLOSED"
LIC_FILES_CHKSUM = ""
SRC_URI = "sftp://hailo@192.168.12.21:/mnt/v02/sdk/validation/vision_app_releases/2024-09-24_18-14-44/vision_control.tar.gz"
SRC_URI[sha256sum] = "9041d4a0f5afc5aafc06083b7bf150f285c084f322729634eaf90c0a1f796297"
ROOTFS_CONFIGS_DIR = "${D}/usr/share/hailo/webpage"
S = "${WORKDIR}/vision_control"
do_install() {
	# install config path on the rootfs
    install -d ${ROOTFS_CONFIGS_DIR}
	    # copy the required files into the config path
    cp -R --no-dereference --preserve=mode,links -v ${S}/* ${ROOTFS_CONFIGS_DIR}
}
FILES:${PN} += " /usr/share/hailo/webpage/*"