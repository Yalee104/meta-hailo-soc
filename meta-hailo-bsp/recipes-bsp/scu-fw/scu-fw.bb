DESCRIPTION = "Hailo SCU. \
               This recipe will download the SCU firmware binary from AWS and add it to deploy"

inherit deploy

LICENSE = "Proprietary"
LIC_FILES_CHKSUM = "file://../LICENSE;md5=263ee034adc02556d59ab1ebdaea2cda"

BASE_URI = "https://hailo-hailort.s3.eu-west-2.amazonaws.com/Hailo15/1.4.1/scu-fw"
FW = "hailo15_scu_fw.bin"
FW_LINK = "${SCU_FW_BASE_BINARY_NAME}"
LICENSE_FILE = "LICENSE"
SRC_URI = "${BASE_URI}/${FW};name=fw \
           ${BASE_URI}/${LICENSE_FILE};name=lic"

SRC_URI[fw.sha256sum] = "4e952ed2492fd4e2f2f00f326ad569d693cc7c84a9164269f41af5435c6d87ce"
SRC_URI[lic.sha256sum] = "ca96445e6e33ae0a82170ea847b0925c864492f0cbb6342d42c54fd647133608"

do_deploy() {
  install -m 644 -D ${WORKDIR}/${FW} ${DEPLOYDIR}/${FW}
	ln -s -r ${DEPLOYDIR}/${FW} ${DEPLOYDIR}/${FW_LINK}
}

# Allows a creation of a package without files. If files are added, this attribute should be removed.
ALLOW_EMPTY:${PN} = "1"

addtask deploy after do_compile
