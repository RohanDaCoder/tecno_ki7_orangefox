#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 The TWRP Open Source Project
# Copyright (C) 2026 RohanDaCoder - TECNO Spark 10 Pro (KI7) device tree
#                              <https://github.com/RohanDaCoder>
#
# SPDX-License-Identifier: Apache-2.0
#
# TWRP/OrangeFox device tree for TECNO Spark 10 Pro (KI7)
# Based on the KH7n OrangeFox tree by isus203 (github.com/tecno-mt6768)
# and SebaUbuntu's twrpdtgen TECNO-KI7 tree.
# All partition sizes and boot header values verified against a live
# KI7 (HiOS KI7-V7510AACDGHJKLMN-T-GL-250218V5302) dump, 2026-11.
#
DEVICE_PATH := device/tecno/KI7

# Allow building with minimal manifest
ALLOW_MISSING_DEPENDENCIES := true

# OTA assert
TARGET_OTA_ASSERT_DEVICE := TECNO-KI7,KI7,ki7

# Architecture (Helio G88 / MT6769H, Cortex-A75 + Cortex-A55, armv8.2)
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 :=
TARGET_CPU_VARIANT := cortex-a55
TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv8-2a
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := cortex-a55
TARGET_BOARD_SUFFIX := _64
TARGET_USES_64_BIT_BINDER := true
TARGET_SUPPORTS_64_BIT_APPS := true

# Enable CPUSets
ENABLE_CPUSETS := true
ENABLE_SCHEDBOOST := true

# A/B (Virtual A/B with compression) - no dedicated recovery partition
AB_OTA_UPDATER := true
TARGET_NO_RECOVERY := true
BOARD_USES_RECOVERY_AS_BOOT := true
BOARD_BUILD_SYSTEM_ROOT_IMAGE := false
BOARD_SUPPRESS_SECURE_ERASE := true

# Bootloader
TARGET_BOOTLOADER_BOARD_NAME := KI7
TARGET_NO_BOOTLOADER := true

# Platform
TARGET_BOARD_PLATFORM := mt6768
PRODUCT_PLATFORM := mt6768
TARGET_USES_UEFI := true

# MTK Hardware
BOARD_HAS_MTK_HARDWARE := true
BOARD_USES_MTK_HARDWARE := true
MTK_HARDWARE := true

# Kernel (values read from the stock boot image header)
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2 buildvariant=user
BOARD_KERNEL_IMAGE_NAME := Image
BOARD_NAME := CY-KI7-V7510
BOARD_KERNEL_PAGESIZE := 2048
BOARD_BOOTIMG_HEADER_VERSION := 2
BOARD_KERNEL_BASE := 0x40078000
BOARD_KERNEL_TAGS_OFFSET := 0x0bc08000
BOARD_KERNEL_OFFSET := 0x00008000
BOARD_KERNEL_SECOND_OFFSET := 0xbff88000
BOARD_RAMDISK_OFFSET := 0x07c08000
BOARD_DTB_OFFSET := 0x0bc08000
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
TARGET_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb
TARGET_KERNEL_ARCH := arm64
# NOTE: do NOT set BOARD_INCLUDE_DTB_IN_BOOTIMG here - with it set, the A12.1
# build system makes boot.img depend on a kernel-built out/.../dtb.img, which
# a prebuilt-kernel tree has no rule for (ninja: "missing and no known rule").
# The DTB is embedded instead via the --dtb mkbootimg argument below (same
# approach as the KH7n tree, whose BOARD_INCLUDE__DTB_IN_BOOTIMG has a typo
# and is therefore effectively unset).
BOARD_MKBOOTIMG_ARGS += --base $(BOARD_KERNEL_BASE)
BOARD_MKBOOTIMG_ARGS += --board $(BOARD_NAME)
BOARD_MKBOOTIMG_ARGS += --pagesize $(BOARD_KERNEL_PAGESIZE)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --kernel_offset $(BOARD_KERNEL_OFFSET)
BOARD_MKBOOTIMG_ARGS += --second_offset $(BOARD_KERNEL_SECOND_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET)
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOTIMG_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)

# AVB - bootloader is unlocked (verifiedbootstate=orange), these flags
# disable verity/verification so the built images boot cleanly.
# NOTE: avb/boot_pubkey.pem is the shared Transsion MT6768 key from the
# KH7n tree; it is not actually required for unlocked devices.
BOARD_AVB_ENABLE := true
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --set_hashtree_disabled_flag
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 2
BOARD_AVB_VBMETA_SYSTEM := system product
BOARD_AVB_VBMETA_SYSTEM_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_SYSTEM_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)
BOARD_AVB_VBMETA_SYSTEM_ROLLBACK_INDEX_LOCATION := 1
BOARD_AVB_VBMETA_VENDOR := vendor
BOARD_AVB_VBMETA_VENDOR_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_VBMETA_VENDOR_ALGORITHM := SHA256_RSA2048
BOARD_AVB_VBMETA_VENDOR_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)
BOARD_AVB_VBMETA_VENDOR_ROLLBACK_INDEX_LOCATION := 2
BOARD_AVB_RECOVERY_KEY_PATH := external/avb/test/data/testkey_rsa2048.pem
BOARD_AVB_RECOVERY_ALGORITHM := SHA256_RSA2048
BOARD_AVB_RECOVERY_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)
BOARD_AVB_RECOVERY_ROLLBACK_INDEX_LOCATION := 3
BOARD_AVB_BOOT_KEY_PATH := $(DEVICE_PATH)/avb/boot_pubkey.pem
BOARD_AVB_BOOT_ALGORITHM := SHA256_RSA2048
BOARD_AVB_BOOT_ROLLBACK_INDEX := $(PLATFORM_SECURITY_PATCH_TIMESTAMP)
BOARD_AVB_BOOT_ROLLBACK_INDEX_LOCATION := 3

# Decryption footer props
BOARD_AVB_RECOVERY_ADD_HASH_FOOTER_ARGS += \
    --prop com.android.build.boot.os_version:$(PLATFORM_VERSION) \
    --prop com.android.build.boot.security_patch:$(PLATFORM_SECURITY_PATCH)

# Anti-rollback hack (keymaster must accept the recovery ramdisk)
PLATFORM_VERSION := 12.0.0
PLATFORM_VERSION_LAST_STABLE := $(PLATFORM_VERSION)
PLATFORM_SECURITY_PATCH := 2099-12-31
VENDOR_SECURITY_PATCH := 2099-12-31

# Treble
BOARD_VNDK_VERSION := current

# Metadata partition (FBE keydirectory lives on md_udc)
BOARD_USES_METADATA_PARTITION := true
BOARD_ROOT_EXTRA_FOLDERS += metadata tranfs

# Partitions
BOARD_FLASH_BLOCK_SIZE := 131072 # (BOARD_KERNEL_PAGESIZE * 64)
BOARD_BOOTIMAGE_PARTITION_SIZE := 33554432
# NOTE: stock boot_a is 32 MiB. vendor_boot_a (64 MiB) and init_boot_a (8 MiB)
# are unused (boot image header v2 keeps the full ramdisk in boot).
# After merging boot_a + vendor_boot_a with the org's repartitioner the size
# becomes 100663296 - change the line above if you repartition.
BOARD_DTBOIMG_PARTITION_SIZE := 8388608
BOARD_HAS_LARGE_FILESYSTEM := true

# Dynamic partitions - REAL values from lpdump on this device:
#   super = 10522669056 bytes, group "main" max = 10520571904 bytes
BOARD_SUPER_PARTITION_SIZE := 10522669056
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 10520571904
BOARD_MAIN_PARTITION_LIST := system vendor product system_ext
# NOTE: PRODUCT_USE_DYNAMIC_PARTITIONS must NOT be set here (board config
# marks it readonly - "cannot assign to readonly variable"); it is set in
# device.mk, where product variables belong.

# File systems
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_F2FS := true
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_VENDOR := vendor

# Disable system mount
TW_NO_BIND_SYSTEM := true

# Recovery
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/system.prop
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery/root/system/etc/recovery.fstab
TARGET_RECOVERY_INITRC := $(DEVICE_PATH)/recovery/root/init.recovery.mt6768.rc

# Init
#TARGET_INIT_VENDOR_LIB := libinit_mtk
#TARGET_RECOVERY_DEVICE_MODULES := libinit_mtk

# Debug
TWRP_INCLUDE_LOGCAT := true
TARGET_USES_LOGD := true

# Fastbootd
TW_INCLUDE_FASTBOOTD := true

# Tools / resetprop and magiskboot
TW_INCLUDE_RESETPROP := true
TW_INCLUDE_LIBRESETPROP := true
TW_INCLUDE_REPACKTOOLS := true
TW_INCLUDE_REPACK_TOOL := true
TW_INCLUDE_FUSE_EXFAT := true
TW_NO_FASTBOOT_BOOT := true
TW_NO_SCREEN_BLANK := true
TARGET_USES_MKE2FS := true
TW_INCLUDE_NTFS_3G := true
TW_USE_TOOLBOX := true
TW_EXCLUDE_TWRPAPP := true
TW_EXCLUDE_APEX := true
TW_EXCLUDE_PYTHON := true
TW_EXCLUDE_NANO := false
TW_EXCLUDE_LPTOOLS := false
TW_EXCLUDE_LPDUMP := false
TW_EXCLUDE_BASH := false
TW_EXCLUDE_TZDATA := false
TW_BACKUP_EXCLUSIONS := /Files/backup
TW_EXTRA_LANGUAGES := true
TW_DEFAULT_LANGUAGE := en_US
TW_SCREEN_BLANK_ON_BOOT := true
TW_SKIP_ADDITIONAL_FSTAB := true

# Density / status bar (1080x2460 panel, max backlight 3750)
TARGET_SCREEN_WIDTH := 1080
TARGET_SCREEN_HEIGHT := 2460
TARGET_SCREEN_DENSITY := 480
TARGET_RECOVERY_LCD_BACKLIGHT_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_BRIGHTNESS_PATH := /sys/class/leds/lcd-backlight/brightness
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_MAX_BRIGHTNESS := 3750
TW_DEFAULT_BRIGHTNESS := 1500
TW_THEME := portrait_hdpi
TW_STATUS_ICONS_ALIGN := center
TW_CUSTOM_CLOCK_POS := 660

# Fix stock .ozip installation
TW_SKIP_COMPATIBILITY_CHECK := true
TW_OZIP_DECRYPT_KEY := 0000

# SELinux
TWHAVE_SELINUX := true
SEPOLICY_IGNORE_NEVERALLOWS := true
SELINUX_IGNORE_NEVERALLOWS := true
BOARD_SEPOLICY_DIRS += sepolicy/recovery

# Crypto - FBE with metadata encryption (Trustonic TEE)
TW_INCLUDE_CRYPTO := true
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true

# Charger mode
BOARD_CHARGER_ENABLE_SUSPEND := true
BOARD_CHARGER_DISABLE_INIT_BLANK := true

# Storage
RECOVERY_SDCARD_ON_DATA := true
TW_EXCLUDE_DEFAULT_USB_INIT := true

# MTP
TW_EXCLUDE_MTP := false
TW_HAS_MTP := true

# USB mounting
TARGET_USE_CUSTOM_LUN_FILE_PATH := /config/usb_gadget/g1/functions/mass_storage.usb0/lun.%d/file

# Device version
ifeq ($(TW_DEVICE_VERSION),)
TW_DEVICE_VERSION=1.0
endif
