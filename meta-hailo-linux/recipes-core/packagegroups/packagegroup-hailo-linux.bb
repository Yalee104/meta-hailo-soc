SUMMARY = "Minimal Hailo Linux requirements"
DESCRIPTION = "The minimal set of packages required to boot the system"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PACKAGEGROUP_DISABLE_COMPLEMENTARY = "1"
PACKAGES = "packagegroup-hailo-linux \
            packagegroup-hailo-linux-dev-pkg"

RDEPENDS:${PN} = "\
    alsa-lib \
    alsa-plugins \
    alsa-state \
    alsa-topology-conf \
    alsa-utils \
    alsa-utils-scripts \
    dosfstools \
    e2fsprogs \
    e2fsprogs-resize2fs \
    ${@bb.utils.contains('MACHINE_FEATURES', 'ddr_ecc_en', 'edac-utils', '', d)} \
    exfat-utils \
    fuse-exfat \
    glibc-binary-localedata-en-us \
    gptfdisk \
    ${@bb.utils.contains('ADD_GSTREAMER_TO_IMAGE', 'true', d.getVar('GSTREAMER_VERSIONS'), '', d)} \
    hailo-base-config \
    kmod \
    libiio \
    libiio-iiod \
    lmsensors-libsensors \
    lmsensors-sensors \
    mmc-utils \
    mtd-utils \
    openssl \
    openssl-bin \
    os-release \
    ${@bb.utils.contains('ADD_PYTHON_TO_IMAGE', 'true', 'python3', '', d)} \
    ${@bb.utils.contains('ADD_PYTHON_NUMPY_TO_IMAGE', 'true', 'python3-numpy', '', d)} \
    sensors-config-file \
    util-linux \
    v4l-utils"

# Development package group
RDEPENDS:${PN}-dev-pkg = "\
    packagegroup-hailo-linux \
    alsa-tools \
    edac-utils \
    ethtool \
    htop \
    libgpiod \
    libgpiod-tools \
    libiio-dbg \
    libiio-dev \
    libiio-tests \
    linux-firmware-rtl-nic \
    lrzsz \
    nfs-utils-client \
    openssh-sftp-server \
    pciutils \
    perf \
    phytool \
    rsync \
    stress-ng \
    ssmtp \
    sysstat \
    tmux \
    tcpdump \
    tree \
    usbutils \
    usbutils-dbg \
    usbutils-dev \
    usbutils-doc \
    usbutils-python \
    vsftpd"
