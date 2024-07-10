FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.3.1"
LINUX_YOCTO_HAILO_SRCREV = "4899c413c587fb52162f07346bad9b73f709d769"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


