DESCRIPTION = "Media Library package recipe \
               compiles medialibrary vision_pre_proc shared object and copies it to usr/lib/ "

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=031eb3f48c82f13ff6cdb783af612501"

SRC_URI = "git://git@github.com/hailo-ai/hailo-media-library.git;protocol=https;branch=1.3.1"
SRCREV = "c17a14ed4a8f6f0e1c4c6c04cfec3d867d4e4b8a"

inherit media-library-base

MEDIA_LIBRARY_BUILD_TARGET = "core"

DEPENDS:append = " gstreamer1.0-plugins-good rapidjson json-schema-validator expected httplib"

# Hailo-15 Dependencies
DEPENDS:append = " video-encoder libhailodsp libhailort"
# Hailo-15 Runtime-Dependencies
RDEPENDS:${PN} += " medialib-configs"

FILES:${PN} += "${libdir}/libdis_library.so ${libdir}/libhailo_media_library_common.so ${libdir}/libhailo_media_library_frontend.so ${libdir}/libhailo_media_library_encoder.so ${libdir}/libhailo_encoder.so ${incdir}/medialibrary/*.hpp"
FILES:${PN}-lib += "${libdir}/libdis_library.so ${libdir}/libhailo_media_library_common.so ${libdir}/libhailo_media_library_frontend.so ${libdir}/libhailo_media_library_encoder.so ${libdir}/libhailo_encoder.so"
