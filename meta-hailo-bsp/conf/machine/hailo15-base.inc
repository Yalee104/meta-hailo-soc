require hailo15-family-base.inc

HAILO_HOST_NAME ??= "hailo15"
hostname:pn-base-files = "${HAILO_HOST_NAME}"

SCU_FW_MACHINE = "${HAILO_HOST_NAME}"
SCU_BL_MACHINE = "${HAILO_HOST_NAME}"
RECOVERY_FW_MACHINE = "${HAILO_HOST_NAME}"
