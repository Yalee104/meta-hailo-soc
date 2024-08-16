FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://fragment.cfg"

LINUX_YOCTO_HAILO_URI = "github.com/Yalee104/linux-yocto-hailo.git"
LINUX_YOCTO_HAILO_BRANCH = "1.4.1"
LINUX_YOCTO_HAILO_SRCREV = "86928534689ca43bdeb50292fd944d91fd50cf81"

LINUX_YOCTO_HAILO_BOARD_VENDOR = "greenbase"


