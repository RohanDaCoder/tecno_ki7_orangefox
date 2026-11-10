#
# Copyright (C) 2022 The OrangeFox Recovery Project
#
# SPDX-License-Identifier: Apache-2.0
#
FDEVICE="KI7"
#set -o xtrace

fox_get_target_device() {
    local chkdev=$(echo "$BASH_SOURCE" | grep -w $FDEVICE)
    if [ -n "$chkdev" ]; then
        FOX_BUILD_DEVICE="$FDEVICE"
    else
        chkdev=$(set | grep BASH_ARGV | grep -w $FDEVICE)
        [ -n "$chkdev" ] && FOX_BUILD_DEVICE="$FDEVICE"
    fi
}

if [ -z "$1" -a -z "$FOX_BUILD_DEVICE" ]; then
    fox_get_target_device
fi

if [ "$1" = "$FDEVICE" -o "$FOX_BUILD_DEVICE" = "$FDEVICE" ]; then
    export TARGET_DEVICE_ALT="TECNO-KI7"
    export FOX_AB_DEVICE=1
    export FOX_RECOVERY_SYSTEM_PARTITION="/dev/block/mapper/system"
    export FOX_RECOVERY_VENDOR_PARTITION="/dev/block/mapper/vendor"
    export OF_DONT_PATCH_ENCRYPTED_DEVICE=1
    export OF_NO_TREBLE_COMPATIBILITY_CHECK=1
    export OF_QUICK_BACKUP_LIST="/boot;/data;/nvram;/proinfo;"
    export FOX_DELETE_AROMAFM=1

    # OrangeFox binary tools (NOTE: these inflate the recovery image -
    # the stock boot partition is only 32 MiB! Either repartition first,
    # or comment out the FOX_USE_* lines below for a slim TWRP-style build)
    export FOX_USE_BASH_SHELL=1
    export FOX_USE_NANO_EDITOR=1
    export FOX_USE_TAR_BINARY=1
    export FOX_USE_SED_BINARY=1
    export FOX_USE_XZ_UTILS=1
    export FOX_ASH_IS_BASH=1
    export OF_ENABLE_LPTOOLS=1

    # OTA
    export OF_KEEP_DM_VERITY=1
    export OF_FIX_OTA_UPDATE_MANUAL_FLASH_ERROR=1
    export OF_DISABLE_MIUI_OTA_BY_DEFAULT=1

    # R12.1 settings
    export FOX_MAINTAINER_PATCH_VERSION=$(date +%y%m%d)
    export FOX_BUILD_TYPE="unofficial"
    export OF_MAINTAINER="KI7-community"

    # Status bar (1080x2460 panel)
    export OF_SCREEN_H=2460

    # Fix decryption on data media
    export OF_FIX_DECRYPTION_ON_DATA_MEDIA=1

    # let's see what are our build VARs
    if [ -n "$FOX_BUILD_LOG_FILE" -a -f "$FOX_BUILD_LOG_FILE" ]; then
        export | grep "FOX" >> $FOX_BUILD_LOG_FILE
        export | grep "OF_" >> $FOX_BUILD_LOG_FILE
        export | grep "TARGET_" >> $FOX_BUILD_LOG_FILE
        export | grep "TW_" >> $FOX_BUILD_LOG_FILE
    fi
fi
