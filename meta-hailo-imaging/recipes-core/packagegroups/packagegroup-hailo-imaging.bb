SUMMARY = "Hailo Imaging requirements"
DESCRIPTION = "The set of packages required to enable Hailo imaging functionality"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PACKAGEGROUP_DISABLE_COMPLEMENTARY = "1"
PACKAGES = "packagegroup-hailo-imaging \
            packagegroup-hailo-imaging-dev-pkg"

RDEPENDS:${PN} = "\
    imaging-sub-system"

RDEPENDS:${PN}-dev-pkg = "\
    imaging-sub-system-ext \
    qtbase"

RDEPENDS:packagegroup-core-buildessential:append = "\
    kernel-module-cdns-csi2rx \
    kernel-module-hailo15-af-monitor \
    kernel-module-hailo15-isp \
    kernel-module-hailo15-pixel-mux \
    kernel-module-hailo15-rxwrapper \
    kernel-module-hailo15-video-cap \
    kernel-module-hailo15-video-out \
    kernel-module-imx334 \
    kernel-module-imx675 \
    kernel-module-imx678 \
    kernel-module-imx715"
