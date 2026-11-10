#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 The TWRP Open Source Project
# Copyright (C) 2026 RohanDaCoder - TECNO Spark 10 Pro (KI7) device tree
#                              <https://github.com/RohanDaCoder>
#
# SPDX-License-Identifier: Apache-2.0
#
# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)

# Installs gsi keys into ramdisk, to boot a developer GSI with verified boot.
$(call inherit-product, $(SRC_TARGET_DIR)/product/gsi_keys.mk)

# Inherit from the KI7 device tree
$(call inherit-product, device/tecno/KI7/device.mk)

# Inherit some common TWRP stuff
$(call inherit-product, vendor/twrp/config/common.mk)

# Device identifier. This must come after all inclusions.
PRODUCT_DEVICE := KI7
PRODUCT_NAME := twrp_KI7
PRODUCT_BRAND := TECNO
PRODUCT_MODEL := KI7
PRODUCT_MANUFACTURER := Tecno Mobility Limited

PRODUCT_BUILD_PROP_OVERRIDES += \
    TARGET_DEVICE=TECNO-KI7 \
    PRODUCT_NAME=KI7-GL \
    PRIVATE_BUILD_DESC="vnd_ki7_v7510-user 12 SP1A.210812.016 250218V3400 release-keys"

BUILD_FINGERPRINT := TECNO/KI7-GL/TECNO-KI7:12/SP1A.210812.016/250218V3400:user/release-keys
