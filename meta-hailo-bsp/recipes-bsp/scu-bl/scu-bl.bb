DESCRIPTION = "Hailo SCU bootloader. \
               This recipe will download the SCU bootloader binary from AWS and add it to deploy"

inherit deploy

LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://../LICENSE;md5=263ee034adc02556d59ab1ebdaea2cda"

BASE_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.3.0/scu-bl"
BL = "hailo15_scu_bl.bin"
LICENSE_FILE = "LICENSE"
SRC_URI = "${BASE_URI}/${BL};name=bl \
           ${BASE_URI}/${LICENSE_FILE};name=lic"

SRC_URI[bl.sha256sum] = "a5e8962b2567b2054b84af69bb38d611a867a6cc181f2b7f16f7d9a5d0c4c356"
SRC_URI[lic.sha256sum] = "ca96445e6e33ae0a82170ea847b0925c864492f0cbb6342d42c54fd647133608"

do_deploy() {
  install -m 644 -D ${WORKDIR}/${BL} ${DEPLOYDIR}/${BL}
}

addtask deploy after do_compile
