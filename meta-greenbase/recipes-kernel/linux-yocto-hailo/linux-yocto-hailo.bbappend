FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.4.0"
LINUX_YOCTO_HAILO_SRCREV = "3dfab70b771ffe8ce5b558acd83af7ae16efdb5a"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


