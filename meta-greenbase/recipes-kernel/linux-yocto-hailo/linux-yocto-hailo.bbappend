FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.5.0"
LINUX_YOCTO_HAILO_SRCREV = "2e48e674c2338a4250c12f16e9a2743e43283b85"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


