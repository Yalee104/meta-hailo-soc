FILESEXTRAPATHS:prepend:hailo15 := "${THISDIR}/files/:"

SRC_URI:append:hailo15 = "file://roundrobin.patch;striplevel=3"
