SUMMARY = "Hailo BSP requirements"
DESCRIPTION = "The set of packages required to enable BSP functionality"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PACKAGEGROUP_DISABLE_COMPLEMENTARY = "1"
PACKAGES = "${PN}"

RDEPENDS:${PN} = "\
    ${@bb.utils.contains('MACHINE_FEATURES', 'disable_load_all_kernel_modules', '', ' kernel-modules', d)} \
    recovery-fw \
    scu-bl \
    scu-fw"
