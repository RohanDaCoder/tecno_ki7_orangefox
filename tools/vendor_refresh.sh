#!/usr/bin/env bash
# =============================================================================
# vendor_refresh.sh - pull the Trustonic TEE / keymaster userspace from the
# LIVE /vendor of your KI7, so the recovery tree uses your exact binaries.
#
# The tree ships the TEE stack from the KH7n (Spark 9 Pro) tree - same
# mt6768 platform and same Trustonic TEE, so it should work - but your own
# firmware may carry slightly newer trustlet/service versions.
#
# HOW TO USE (in Termux on the phone, rooted):
#   bash vendor_refresh.sh        # writes $HOME/ki7_tee_vendor.tar.gz
#
# Then on your PC, extract it OVER recovery/root/vendor/ in this tree:
#   tar xzf ki7_tee_vendor.tar.gz -C android_device_tecno_KI7/recovery/root/
# and rebuild.
# =============================================================================
set -u

if [ "$(id -u)" != "0" ]; then
    echo "[*] re-running as root via sudo..."
    exec sudo bash "$0" "$@"
fi

OUT="${OUT:-/data/data/com.termux/files/home/ki7_tee_vendor.tar.gz}"
TERMUX_HOME=/data/data/com.termux/files/home

FILES=()
add() { [ -e "/$1" ] && FILES+=("$1") || echo "  [skip] /$1 (not present)"; }
add_dir() {
    if [ -d "/$1" ]; then
        while IFS= read -r f; do FILES+=("${f#/}"); done < <(cd / && find "$1" -type f)
    else
        echo "  [skip] /$1 (not present)"
    fi
}

echo "[*] collecting TEE / keymaster files from /vendor ..."

# TEE daemon & HAL services
add vendor/bin/mcDriverDaemon
add vendor/bin/android.hardware.keymaster@4.1-service.trustonic
add vendor/bin/android.hardware.gatekeeper@1.0-service
add vendor/bin/vendor.trustonic.tee@1.1-service
add vendor/bin/kmsetkey_ca.trustonic
add vendor/bin/vendor.mediatek.hardware.keymaster_attestation@1.1-service
add vendor/bin/vendor.mediatek.hardware.paytrigger@1.0-service

# Trustlet registry (needed by mcDriverDaemon)
add_dir vendor/app/mcRegistry

# Keymaster / TEE libraries
for l in \
    android.hardware.keymaster@3.0.so \
    android.hardware.keymaster@4.0.so \
    android.hardware.keymaster@4.1.so \
    libMcClient.so \
    libTEECommon.so \
    libhwbinder.so \
    libimsg_log.so \
    libion_mtk.so \
    libion_ulit.so \
    libkeymaster4.so \
    libkeymaster41.so \
    libkeymaster4_1support.so \
    libkeymaster4support.so \
    libkeymaster_messages.so \
    libkeymaster_portable.so \
    libkmsetkey.so \
    libladder.so \
    libmtk_bsg.so \
    libpuresoftkeymasterdevice.so \
    liburee_meta_drmkeyinstall.so \
    vendor.mediatek.hardware.keymaster_attestation@1.0.so \
    vendor.mediatek.hardware.keymaster_attestation@1.1.so \
    vendor.mediatek.hardware.paytrigger@1.0.so \
    vendor.trustonic.tee.tui@1.0.so \
    vendor.trustonic.tee@1.0.so \
    vendor.trustonic.tee@1.1.so
do
    add "vendor/lib64/$l"
done

# HAL implementations
for h in \
    android.hardware.gatekeeper@1.0-impl.so \
    gatekeeper.default.so \
    gatekeeper.trustonic.so \
    kmsetkey.default.so \
    kmsetkey.trustonic.so \
    libMcGatekeeper.so \
    libSoftGatekeeper.so \
    paytrigger.trustonic.so \
    vendor.mediatek.hardware.keymaster_attestation@1.1-impl.so \
    hwcomposer.mt6768.so
do
    add "vendor/lib64/hw/$h"
done

# Trustonic trusted applications
add_dir vendor/thh/ta

# Firmware (touchpanel/BT/WiFi/haptics - wrong-device firmware can break
# touch in recovery, so pulling YOUR set is a good idea)
add_dir vendor/firmware

# VINTF manifests (hwservicemanager registration)
add vendor/etc/vintf/manifest.xml
add vendor/etc/vintf/compatibility_matrix.xml
add_dir vendor/etc/vintf/manifest

echo "[*] packing ${#FILES[@]} files -> $OUT"
cd / && tar czf "$OUT" "${FILES[@]}"

# hand the archive back to the termux user
OWNER=$(stat -c '%u:%g' "$TERMUX_HOME" 2>/dev/null || echo "0:0")
chown "$OWNER" "$OUT" 2>/dev/null || true

echo "[+] done: $OUT"
echo "    (adb pull it, then extract over recovery/root/vendor/ in the tree and rebuild)"
