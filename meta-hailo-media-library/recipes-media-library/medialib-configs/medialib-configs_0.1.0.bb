DESCRIPTION = "Media Library Configuration files recipe \
               fetches the configuration files for the media library and sets hierarchy in /usr/lib"

LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://${WORKDIR}/media-library/LICENSE;md5=263ee034adc02556d59ab1ebdaea2cda"

SRC_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.3.0-dev/media-library.tar.gz"
SRC_URI[sha256sum] = "d654315b190d84e370ce4a4ca36cd9611fa654e4caab28c4610a559003c19af2"

S = "${WORKDIR}/media-library/medialib"

ROOTFS_CONFIGS_DIR = "${D}/usr/lib/medialib/"

do_install() {
	# install config path on the rootfs
    install -d ${ROOTFS_CONFIGS_DIR}

    # copy the required files into the config path
    cp -R --no-dereference --preserve=mode,links -v ${S}/* ${ROOTFS_CONFIGS_DIR}
}

FILES:${PN} += " /usr/lib/medialib/*"
