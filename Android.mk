#
# Copyright (C) 2020 The Android Open Source Project
# Copyright (C) 2020 The TWRP Open Source Project
# Copyright (C) 2026 RohanDaCoder - TECNO Spark 10 Pro (KI7) device tree
#                              <https://github.com/RohanDaCoder>
#
# SPDX-License-Identifier: Apache-2.0
#
LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),KI7)
include $(call all-subdir-makefiles,$(LOCAL_PATH))
endif
