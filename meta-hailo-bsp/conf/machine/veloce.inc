FIT_KERNEL_COMP_ALG = "none"
FIT_KERNEL_COMP_ALG_EXTENSION = ""

# disable SSH in veloce since it causes key generation at boot time which slows down the boot
EXTRA_IMAGE_FEATURES:remove = "${SSH_SERVER_FEATURES}"
