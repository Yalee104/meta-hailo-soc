# Patch to fix the removal of branch master from libiio.
SRCREV = "92d6a35f3d8d721cda7d6fe664b435311dd368b4"

SRC_URI = "git://github.com/analogdevicesinc/libiio.git;protocol=https;branch=main \
           file://0001-CMake-Move-include-CheckCSourceCompiles-before-its-m.patch \
"
