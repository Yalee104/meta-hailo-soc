FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.5.1"
LINUX_YOCTO_HAILO_SRCREV = "d262c76e361c3edc02426467bc9243a3555e72fc"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


