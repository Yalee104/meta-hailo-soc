FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.4.0"
LINUX_YOCTO_HAILO_SRCREV = "4a329ad96fa29908714eda3cfb30f0000db16343"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


