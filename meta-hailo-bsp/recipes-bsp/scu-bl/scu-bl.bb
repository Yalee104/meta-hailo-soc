DESCRIPTION = "Hailo SCU bootloader. \
               This recipe will download the SCU bootloader binary from AWS and add it to deploy"

inherit deploy

LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://../LICENSE;md5=263ee034adc02556d59ab1ebdaea2cda"

BASE_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.4.0/scu-bl"
BL = "${SCU_BL_BINARY_NAME}"
LICENSE_FILE = "LICENSE"
CONFIG_JSON_A = "scu_bl_cfg_a.json"
CONFIG_JSON_B = "scu_bl_cfg_b.json"
scu_bl_cfg_targetdir = "/etc/scu_bl_cfg"
CONFIG_BIN_A = "scu_bl_cfg_a.bin"
CONFIG_BIN_B = "scu_bl_cfg_b.bin"
CONFIG_MANAGER_PY = "scu_bootloader_config_manager.py"

BL_FILES = "${BASE_URI}/${BL};name=bl ${BASE_URI}/${LICENSE_FILE};name=lic"
SRC_URI = "file://scu_bootloader_config_manager.py \
           file://scu_bl_cfg_a.json \
           file://scu_bl_cfg_b.json \
           ${BL_FILES}"

SRC_URI[bl.sha256sum] = "60cb4dd029d27ea861bec212eeae5d7b25efb3343e957fd89df19f0fbe360bd1"
SRC_URI[lic.sha256sum] = "ca96445e6e33ae0a82170ea847b0925c864492f0cbb6342d42c54fd647133608"

do_install() {
  ${WORKDIR}/${CONFIG_MANAGER_PY} --scu-bl-cfg-json ${WORKDIR}/${CONFIG_JSON_A} --scu-bl-cfg-bin ${WORKDIR}/${CONFIG_BIN_A}  
  ${WORKDIR}/${CONFIG_MANAGER_PY} --scu-bl-cfg-json ${WORKDIR}/${CONFIG_JSON_B} --scu-bl-cfg-bin ${WORKDIR}/${CONFIG_BIN_B}  

  install -m 0755 -d ${D}${scu_bl_cfg_targetdir}
  install -m 0500 ${WORKDIR}/${CONFIG_BIN_A} ${D}${scu_bl_cfg_targetdir}
  install -m 0500 ${WORKDIR}/${CONFIG_BIN_B} ${D}${scu_bl_cfg_targetdir}
}

do_deploy() {
  install -m 644 -D ${WORKDIR}/${BL} ${DEPLOYDIR}/${BL}
  install -m 644 -D ${WORKDIR}/${CONFIG_BIN_A} ${DEPLOYDIR}/${CONFIG_BIN_A}
  install -m 644 -D ${WORKDIR}/${CONFIG_BIN_B} ${DEPLOYDIR}/${CONFIG_BIN_B}
}

FILES:${PN} += "${scu_bl_cfg_targetdir}/scu_bl_cfg_a.bin"
FILES:${PN} += "${scu_bl_cfg_targetdir}/scu_bl_cfg_b.bin"

PACKAGES = "${PN} ${PN}-dev"
ALLOW_EMPTY:${PN} = "1"

addtask deploy after do_compile
