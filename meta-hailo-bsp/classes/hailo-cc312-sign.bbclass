# This class is used for signing binary files for authentication using cryptocell-312
# by Hailo-15 SCU.
#

DEPENDS += "cryptocell-312-runtime-native"
DEPENDS += "hailo-secureboot-assets"
DEPENDS += "hailo-secureboot-scripts-native"
DEPENDS += "gettext-native"

CERT_KEYPAIR ?= "${DEPLOY_DIR_IMAGE}/customer.key"
ROT_KEYPAIR ?= "${DEPLOY_DIR_IMAGE}/customer_rot.key"
KEY_CERTIFICATE ?= "${DEPLOY_DIR_IMAGE}/key_certificate.bin"
CC312_DIR ?= "${STAGING_ETCDIR_NATIVE}/cc312"

# Sign a binary file using the Hailo-15 SCU boot image signing tool
# Arguments:
# 1. unsigned_binary: The path to the binary file to sign
# 2. binary_type: The type of the binary file to sign - one of "image", "devicetree"
# 3. signed_binary: The path to the signed binary file
hailo15_boot_image_sign() {
    unsigned_binary=$1
    binary_type=$2
    signed_binary=$3
    hailo15_boot_image_sign.sh ${CC312_DIR} ${CERT_KEYPAIR} ${unsigned_binary} ${binary_type} ${signed_binary}
}

# Sign a firmware file for the SCU processor (SCU-FW, SCU-BL, Uart Recovery FW)
# Arguments:
# 1. unsigned_firmware: The path to the firmware file to sign
# 2. signed_firmware: The path to the signed firmware file
hailo15_scu_firmware_sign() {
    unsigned_firmware=$1
    signed_firmware=$2
    hailo15_scu_image_sign.sh ${CC312_DIR} ${KEY_CERTIFICATE} ${CERT_KEYPAIR} ${unsigned_firmware} ${signed_firmware}
}
