#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 The TWRP Open Source Project
# Copyright (C) 2026 RohanDaCoder - TECNO Spark 10 Pro (KI7) device tree
#                              <https://github.com/RohanDaCoder>
#
# SPDX-License-Identifier: Apache-2.0
#
LOCAL_PATH := device/tecno/KI7

# Dynamic partitions
PRODUCT_USE_DYNAMIC_PARTITIONS := true

# Enable updating of APEXes
$(call inherit-product, $(SRC_TARGET_DIR)/product/updatable_apex.mk)

# Virtual A/B (with compression - as shipped on KI7)
ENABLE_VIRTUAL_AB := true
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/launch.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/compression.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota/compression_retrofit.mk)

# A/B partitions as present on the device (from /dev/block/by-name)
AB_OTA_PARTITIONS += \
    boot \
    dtbo \
    gz \
    lk \
    logo \
    md1img \
    product \
    scp \
    spmfw \
    sspm \
    system \
    system_ext \
    tee \
    vendor \
    vbmeta \
    vbmeta_system \
    vbmeta_vendor

AB_OTA_POSTINSTALL_CONFIG += \
    RUN_POSTINSTALL_system=true \
    POSTINSTALL_PATH_system=system/bin/otapreopt_script \
    FILESYSTEM_TYPE_system=ext4 \
    POSTINSTALL_OPTIONAL_system=true

AB_OTA_POSTINSTALL_CONFIG += \
    RUN_POSTINSTALL_vendor=true \
    POSTINSTALL_PATH_vendor=bin/checkpoint_gc \
    FILESYSTEM_TYPE_vendor=ext4 \
    POSTINSTALL_OPTIONAL_vendor=true

ENABLE_VIRTUAL_AB := true
PRODUCT_VIRTUAL_AB_OTA := true
PRODUCT_VENDOR_PROPERTIES += ro.virtual_ab.enabled=true

# Fastbootd
PRODUCT_PACKAGES += \
    android.hardware.fastboot@1.0-impl-mock \
    fastbootd

# Health HAL
PRODUCT_PACKAGES += \
    android.hardware.health@2.1-impl \
    android.hardware.health@2.1-service

# Bootctrl (MTK)
PRODUCT_PACKAGES += \
    android.hardware.boot@1.2-mtkimpl \
    android.hardware.boot@1.2-mtkimpl.recovery
PRODUCT_PACKAGES_DEBUG += \
    bootctrl

# MTK plpath utils (preloader raw symlink helper)
PRODUCT_PACKAGES += \
    mtk_plpath_utils \
    mtk_plpath_utils.recovery

# VNDK / API levels (vendor image is Android 12 / API 31)
# Live dump: ro.board.first_api_level=30, ro.product.first_api_level=33
PRODUCT_TARGET_VNDK_VERSION := 31
PRODUCT_SHIPPING_API_LEVEL := 33
BOARD_SHIPPING_API_LEVEL := 30

PRODUCT_PACKAGES_DEBUG += \
    update_engine_client
PRODUCT_PACKAGES += \
    otapreopt_script \
    cppreopts.sh \
    checkpoint_gc \
    update_engine \
    update_verifier \
    update_engine_sideload

# Additional binaries & libraries needed for recovery (FBE decryption)
TARGET_RECOVERY_DEVICE_MODULES += \
    libgatekeeper \
    libgatekeeper_aidl \
    libkeymaster41 \
    libpuresoftkeymasterdevice
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += \
    $(TARGET_OUT_SHARED_LIBRARIES)/libgatekeeper.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libgatekeeper_aidl.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libkeymaster41.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libpuresoftkeymasterdevice.so

# Take a few libraries from sources
TARGET_RECOVERY_DEVICE_MODULES += \
    android.hidl.allocator@1.0 \
    android.hidl.memory@1.0 \
    android.hidl.memory.token@1.0 \
    libdmabufheap \
    libhidlmemory \
    libion
RECOVERY_LIBRARY_SOURCE_FILES += \
    $(TARGET_OUT_SHARED_LIBRARIES)/android.hidl.allocator@1.0.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/android.hidl.memory@1.0.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/android.hidl.memory.token@1.0.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libdmabufheap.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libhidlmemory.so \
    $(TARGET_OUT_SHARED_LIBRARIES)/libion.so
