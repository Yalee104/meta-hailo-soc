FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.4.0"
LINUX_YOCTO_HAILO_SRCREV = "a0eab8abf2eff9f3f54c193aaeb6096297df4160"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


