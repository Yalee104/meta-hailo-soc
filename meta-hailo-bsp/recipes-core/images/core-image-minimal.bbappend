CORE_IMAGE_EXTRA_INSTALL:append = " kernel-modules"
CORE_IMAGE_EXTRA_INSTALL:remove = "${@bb.utils.contains('MACHINE_FEATURES', 'disable_load_all_kernel_modules', ' kernel-modules', '', d)}"
