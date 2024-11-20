DESCRIPTION = "Media Library Configuration files recipe \
               fetches the configuration files for the media library and sets hierarchy in /usr/lib"

S = "${WORKDIR}/git"
RESOURCES_DIR = "${S}/resources"
LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://${RESOURCES_DIR}/sensors/LICENSE;md5=263ee034adc02556d59ab1ebdaea2cda"

SRC_URI = "git://git@github.com/hailo-ai/hailo-media-library.git;protocol=https;branch=1.5.1"
SRC_URI += "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.5.1/hefs.tar.gz;name=hefs"
SRCREV = "ed235d6f7418e11a9e39c5c3d3ba044235c60e42"
SRC_URI[hefs.sha256sum] = "479345ba63e0da7c6653837600620ad1495c2331b2ebf35b59085abf4790cfa9"

HEFS_DIR = "${WORKDIR}/hefs"

ROOTFS_APPS_DIR = "/home/root/apps"
ROOTFS_HOME_DIR = "/home/root"
ROOTFS_CONFIGS_DIR = "${D}/usr/lib/medialib/"
FHD_PROFILE_PATH = "default/fhd/isp_profiles/default"
DEFAULT_PROFILE_PATH = "default/default/isp_profiles/default"

do_install() {
    install -d ${ROOTFS_CONFIGS_DIR}
    
    # Copy the extracted files into the config path
    cp -R --no-dereference --preserve=mode,links -v ${RESOURCES_DIR}/* ${ROOTFS_CONFIGS_DIR}
    cp -R --no-dereference --preserve=mode,links -v ${HEFS_DIR}/* ${ROOTFS_CONFIGS_DIR}

    # copy media library resources
    install -d ${D}/${ROOTFS_APPS_DIR}/resources
    find ${RESOURCES_DIR} -name '*cam_intrinsics*.txt' -exec \
        install -m 0755 {} ${D}/${ROOTFS_APPS_DIR}/resources/ \;
    install -m 0755 ${RESOURCES_DIR}/sensors/imx678/${DEFAULT_PROFILE_PATH}/cam_intrinsics_678.txt \
        ${D}/${ROOTFS_APPS_DIR}/resources/cam_intrinsics.txt
}

FILES:${PN} += " /usr/lib/medialib/* ${ROOTFS_APPS_DIR}/resources/*"
