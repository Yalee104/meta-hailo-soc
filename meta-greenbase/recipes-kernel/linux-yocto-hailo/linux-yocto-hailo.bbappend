FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.4.2"
LINUX_YOCTO_HAILO_SRCREV = "a63c90ea2f30bae3b701dedd1dfeebfd3b689cd8"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


