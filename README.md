# OrangeFox R12.1 / TWRP 12.1 for TECNO Spark 10 Pro (KI7)

**Maintainer:** [RohanDaCoder](https://github.com/RohanDaCoder) (AL Zami Rohan)

[![Build](https://github.com/RohanDaCoder/tecno_ki7_orangefox/actions/workflows/fox-build.yml/badge.svg?branch=Fox_12.1)](https://github.com/RohanDaCoder/tecno_ki7_orangefox/actions/workflows/fox-build.yml)
[![Releases](https://img.shields.io/github/v/release/RohanDaCoder/tecno_ki7_orangefox?include_prereleases&label=release)](https://github.com/RohanDaCoder/tecno_ki7_orangefox/releases)

Ready-to-build OrangeFox R12.1 / TWRP 12.1 device tree for the Tecno Spark 10 Pro
(codename **KI7**, board `CY-KI7-V7510`).

Every board value in this tree was verified against a **live dump** of a rooted KI7
(HiOS `KI7-V7510AACDGHJKLMN-T-GL-250218V5302`, Feb 2025 firmware): boot image header,
partition table, super layout (`lpdump`), stock fstab, display, and kernel blob.

Repo: <https://github.com/RohanDaCoder/tecno_ki7_orangefox> (branch `Fox_12.1`)

## Automated builds (GitHub Actions)

The repo ships CI (`.github/workflows/fox-build.yml`) that builds OrangeFox R12.1
for the KI7 on every push - no local setup needed:

- **Normal commits** (push to `Fox_12.1` / `main`, or a manual *Run workflow*):
  the recovery image is built and stored as a **workflow artifact**
  (repo → *Actions* → the run → *Artifacts*, kept for 30 days).
- **Releases:** push a tag that starts with `v` and CI cuts a full **GitHub
  Release** with the image, its md5 and a bundle zip:

  ```bash
  git tag v1.0
  git push origin v1.0
  ```

The build uses the official OrangeFox sync script (minimal TWRP 12.1 manifest +
OrangeFox build system), pinned to `ubuntu-22.04`, and checks the image against
the stock 32 MiB `boot_a` limit (oversized images are flagged in the artifact's
`build_info.txt` / release notes). Expect ~2.5-4 h per build on the free
public-repo runners.

## Device

Basic | Spec Sheet
-----:|:------------------------
SoC | MediaTek Helio G88 (MT6769H, platform `mt6768`)
CPU | 2x Cortex-A75 @2.0GHz + 6x Cortex-A55 (armv8.2)
GPU | Mali-G52 MC2
Kernel | 4.19.191 (stock, prebuilt - included in `prebuilt/`)
OS | Android 13 system / Android 12 vendor (TSSI)
Display | 6.8" 1080x2460 @ density 480, max backlight 3750
Battery | 5000 mAh
Slots | A/B, **Virtual A/B + compression** (`ro.virtual_ab.enabled=true`)
Crypto | **FBE** + metadata encryption (keydirectory on `md_udc`), Trustonic TEE
Boot image | header **v2**, board name `CY-KI7-V7510`, page 2048, base 0x40078000, ramdisk 0x07c08000, tags 0x0bc08000, dtb 0x0bc08000

### Partition layout (verified with `lpdump` / `/proc/partitions`)

Partition | Size | Notes
---:|---:|---
boot_a | 33,554,432 (32 MiB) | **recovery-as-boot**, active slot: kernel + dual-purpose ramdisk (normal init + `system/bin/recovery`)
boot_b | 8,388,608 (8 MiB) | **too small for any A12.1 recovery image** - asymmetric Transsion GPT; never flash recovery here
vendor_boot_a | 67,108,864 (64 MiB) | **unused** (boot header v2) - merge candidate for repartition
vendor_boot_b | 8,388,608 (8 MiB) | **unused** (boot header v2)
init_boot_a / _b | 8,388,608 (8 MiB) | **unused** (boot header v2)
dtbo_a / _b | 8,388,608 (8 MiB) | MTK DTBO container (magic `d7b7ab1e`)
super | 10,522,669,056 | group `main`, max 10,520,571,904: system, vendor, product, system_ext (+cow)
userdata | f2fs, FBE | `fileencryption=aes-256-xts:aes-256-cts:v2`, keydirectory `/metadata/vold/metadata_encryption`
metadata | `md_udc` | FBE metadata/keydirectory
preloader | `mmcblk0boot0/1` | 4 MiB each

There is **no dedicated recovery partition**. The stock `boot.img` ramdisk contains
both the normal boot init and the HiOS recovery binary (`system/bin/recovery`,
`system/etc/recovery.fstab`, `system/lib64/librecovery_ui.so`). The bootloader picks
recovery vs normal via `androidboot.force_normal_boot`.

## Tree layout

```
tecno_ki7_orangefox/   # clone as device/tecno/KI7
├── .github/workflows/fox-build.yml                    # CI: artifacts on push, release on v* tags
├── manifests/fox_12.1.xml                            # local_manifest for repo sync
├── AndroidProducts.mk / twrp_KI7.mk / Android.mk      # lunch: twrp_KI7-userdebug
├── BoardConfig.mk                                     # all verified KI7 values
├── device.mk                                          # Virtual A/B, bootctrl, TEE relinks
├── system.prop / vendorsetup.sh                       # OrangeFox env vars (OF_SCREEN_H=2460)
├── prebuilt/                                          # kernel (gzip Image), dtb, dtbo.img
│                                                      #   from the live dump - byte-identical
│                                                      #   to the twrpdtgen A12 firmware dump
├── recovery/root/
│   ├── first_stage_ramdisk/fstab.mt6768               # stock KI7 first-stage fstab
│   ├── init.recovery.mt6768.rc                        # MTK init + Trustonic TEE services
│   ├── init.recovery.tee.rc / init.recovery.trustonic.rc
│   ├── init.recovery.usb.rc / ueventd.mt6768.rc
│   ├── system/etc/recovery.fstab + twrp.flags         # KI7 by-name verified
│   ├── system/lib64/                                  # keymaster/gatekeeper relink libs
│   └── vendor/                                        # full Trustonic TEE userspace
│       ├── bin/          (mcDriverDaemon, keymaster@4.1-service.trustonic, ...)
│       ├── app/mcRegistry/  (trustlets .drbin/.tlbin/.tabin)
│       ├── lib64/ + lib64/hw/  (keymaster, gatekeeper, hwcomposer.mt6768)
│       └── thh/ta/       (trusted apps)
├── bootctrl/             # android.hardware.boot@1.2-mtkimpl (source)
├── mtk_plpath_utils/     # preloader raw-link helper (source)
├── avb/boot_pubkey.pem   # Transsion MT6768 AVB key (from the KH7n tree)
├── sepolicy/recovery/    # recovery.te allow rules
└── tools/vendor_refresh.sh  # pull YOUR /vendor TEE blobs from the live phone
```

`recovery/root/vendor` is taken from the KH7n (Spark 9 Pro) tree - same platform,
same Trustonic TEE. If decryption misbehaves, run `tools/vendor_refresh.sh` on the
phone and drop your own blobs in (see below).

## Building

Requirements: Linux x86_64 (Ubuntu 20.04/22.04), 16 GB+ RAM, ~250 GB disk,
standard Android build prerequisites (`repo`, `git`, build-essential, etc.).

### TWRP (recommended first build - fits the stock 32 MiB boot)

```bash
mkdir ~/twrp && cd ~/twrp
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1

# pull in the KI7 device tree:
mkdir -p .repo/local_manifests
curl -o .repo/local_manifests/tecno_ki7.xml \
  https://raw.githubusercontent.com/RohanDaCoder/tecno_ki7_orangefox/Fox_12.1/manifests/fox_12.1.xml

repo sync -c --no-clone-bundle --no-tags -j8

source build/envsetup.sh
lunch twrp_KI7-userdebug
mka recoveryimage -j$(nproc)
```

Output: `out/target/product/KI7/boot.img` (this IS the recovery image - recovery-as-boot).

### OrangeFox R12.1

OrangeFox no longer publishes a standalone `fox_12.1` manifest - the official
method is their sync script, which patches a minimal TWRP 12.1 AOSP manifest
and layers the OrangeFox build system on top:

```bash
mkdir ~/OrangeFox_sync && cd ~/OrangeFox_sync
git clone https://gitlab.com/OrangeFox/sync.git
cd sync
./orangefox_sync.sh --branch 12.1 --path ~/fox_12.1

git clone https://github.com/RohanDaCoder/tecno_ki7_orangefox.git \
    -b Fox_12.1 ~/fox_12.1/device/tecno/KI7

cd ~/fox_12.1
export LC_ALL=C
export ALLOW_MISSING_DEPENDENCIES=true
source build/envsetup.sh
source device/tecno/KI7/vendorsetup.sh KI7
lunch twrp_KI7-eng
mka adbd bootimage
```

`mka adbd bootimage` (not `recoveryimage`) because the KI7 is a **virtual A/B,
recovery-as-boot** device with no dedicated recovery partition - per the
[OrangeFox wiki](https://wiki.orangefox.tech/dev/building).

Output: `out/target/product/KI7/OrangeFox-*.img` (or `boot.img`) - this IS the
recovery image; flash it to `boot_a`.

`vendorsetup.sh` (FOX_*/OF_* env vars, incl. `OF_MAINTAINER=RohanDaCoder`)
must be sourced **manually** before `lunch`, as shown above.

Or just let [GitHub Actions](#automated-builds-github-actions) build it.

### The 32 MiB boot problem (READ THIS)

The stock `boot` partition is only **32 MiB**. A slim TWRP fits (~25-30 MB).
OrangeFox with the default extras (bash, nano, xz, tar, ...) usually does **not**.

- The tree now ships `BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296` (Option C below):
  OrangeFox R12.1 does not fit the stock 32 MiB `boot_a` even when slimmed, so the
  build targets a repartitioned 96 MiB boot. CI flags the image size against the
  stock 32 MiB limit - you MUST repartition before flashing (Option C).
- To chase a 32 MiB image anyway: set `BOARD_BOOTIMAGE_PARTITION_SIZE := 33554432`,
  trim `TW_EXTRA_LANGUAGES`, `TW_INCLUDE_NTFS_3G`, `TW_INCLUDE_FUSE_EXFAT`,
  `TW_EXCLUDE_BASH := true`, and in `vendorsetup.sh` comment out the `FOX_USE_*`
  lines - expect to strip OrangeFox close to bare TWRP to fit.

## Flashing

**First, make a safety net** (you have root):

```bash
adb shell su -c "dd if=/dev/block/by-name/boot_a of=/sdcard/stock_boot_a.img"
adb pull /sdcard/stock_boot_a.img   # keep this forever
```

Your rescue options if anything goes wrong: `mtkclient` (Helio G88 bootrom is
exploitable - can flash any partition via BROM mode), SP Flash Tool with the stock
ROM from needrom.com, or fastboot. You also already hold a full safety net from the
dump session - `boot.img`, `dtbo.img`, `vbmeta*.img` and `ins_preloader.img` -
keep them somewhere safe.

### How recovery works on KI7 (read this - it is NOT the usual slot dance)

A TWRP/OrangeFox `boot.img` contains a recovery-only ramdisk. The stock boot
image is dual-purpose (normal boot + recovery); a custom recovery image is not:
flash it to the active slot and every boot lands in recovery until you reflash
stock.

**KI7's slots are asymmetric** (verified on this device from the GPT):

| partition | size | what it means |
|---|---|---|
| `boot_a` (active) | 32 MiB | the only slot big enough - flash the recovery here |
| `boot_b` | 8 MiB | **a TWRP/OrangeFox image does NOT fit** - never flash recovery here |

So the classic "put TWRP on the inactive slot" trick is impossible on KI7.
The workflow is: flash TWRP to `boot_a` when you need it, reflash the stock
boot image afterwards. Your active slot is `_a` (check:
`getprop ro.boot.slot_suffix`) - re-check after every OTA, because an OTA that
flips the active slot to `b` changes the whole picture.

### Option A - flash TWRP to boot_a (the only real option)

Keep a copy of the stock boot image around - forever:

```bash
adb shell su -c "dd if=/dev/block/by-name/boot_a of=/sdcard/stock_boot_a.img"
adb pull /sdcard/stock_boot_a.img
```

Flash TWRP:

```bash
adb push out/target/product/KI7/boot.img /sdcard/twrp.img
adb shell su -c "dd if=/sdcard/twrp.img of=/dev/block/by-name/boot_a"
adb reboot recovery
```

To return to HiOS, reflash the stock image - from TWRP:

```
TWRP -> Install -> Install Image -> stock_boot_a.img -> target: Boot
```

or from the recovery adb shell:

```bash
adb shell dd if=/sdcard/stock_boot_a.img of=/dev/block/by-name/boot_a
```

then reboot. (The dumped stock image is Magisk-patched - i.e. exactly what the
phone runs today, with root - so HiOS comes back rooted, as before.)

> If an HiOS OTA was installed recently, let it boot several times so the
> Virtual A/B snapshot (COW) fully merges before overwriting `boot_a`.

### Option B - temporary / testing

```bash
adb reboot bootloader
fastboot boot out/target/product/KI7/boot.img    # TRY this first - often blocked on Transsion
```

If `fastboot boot` is blocked (common on Tecno), fall back to Option A.

### Option C - repartition boot to 96 MiB (for full OrangeFox)

`boot_a` (32 MiB) is directly followed by the **unused** `vendor_boot_a` (64 MiB) -
same layout as KH7n, where the same org publishes a working repartitioner:

https://github.com/tecno-mt6768/Universal-Boot-Repartitioner-GPT-Backup
https://github.com/tecno-mt6768/Re-partitioning-kh7n

Requirements: kernel 4.1x (KI7 = 4.19 OK), `vendor_boot` empty/unused (true on KI7 -
header v2 boot), `boot` and `vendor_boot` adjacent (true: p30/p31 and p44/p45).
The tool merges them (32 + 64 = 96 MiB), backs up the original GPT to a restore zip
(you need an SD card for it), and flashes the new boot.img.

After repartitioning set `BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296` and rebuild.
**Only do this after you have TWRP working and a GPT backup.** A botched GPT edit =
hard brick (recoverable only via BROM/mtkclient or SP Flash Tool).

### If you flashed TWRP to boot_b by accident

Not catastrophic: `boot_b` is inactive and only 8 MiB, so the image was truncated
there and slot B is not bootable this way anyway. Do not switch the active slot to
`b` afterwards, and re-check `ro.boot.slot_suffix` before the next OTA. A future
OTA (or mtkclient) can rewrite `boot_b` properly.

## Refreshing the TEE blobs (decryption)

The tree ships the KH7n Trustonic stack. If `/data` doesn't decrypt:

```bash
# on the phone, in Termux:
bash tools/vendor_refresh.sh            # makes ~/ki7_tee_vendor.tar.gz
cp ~/ki7_tee_vendor.tar.gz /sdcard/     # (or scp it out directly - you have sshd)
adb pull /sdcard/ki7_tee_vendor.tar.gz

# on the PC, in the tree:
tar xzf ki7_tee_vendor.tar.gz -C recovery/root/
# rebuild & reflash
```

Decryption expectations: FBE + metadata + Trustonic on an Android 12-based recovery
is the hardest combination - it may take a few iterations (correct libs, correct
order of services). Everything else (flash, backup, restore, wipe) works even
without decryption.

## Known limitations / notes

- **`fastboot boot`** is usually blocked by the Transsion bootloader - expect
  `FAILED (remote: unknown command)`; use the slot method.
- **Orange state warning** (unlocked bootloader) on every boot is cosmetic.
- Flashing a vbmeta with `--flags 3` / `--disable-verity --disable-verification`
  is not required while the bootloader is unlocked and verified boot is orange.
- Virtual A/B + compression: TWRP 12.1 handles the COW device; avoid wiping
  `metadata` unless you know what you're doing.
- `vendor_boot`/`init_boot` entries in `twrp.flags` exist for completeness - those
  partitions are unused on KI7 (header v2). Do not flash them.
- The kernel in `prebuilt/` was extracted from a **Magisk-patched** boot image.
  The kernel and DTB blobs are untouched by Magisk (only the ramdisk is patched)
  and are byte-identical to the stock A12 firmware blobs, so they're safe to use.

## Credits

- **RohanDaCoder** - current maintainer of this tree. https://github.com/RohanDaCoder
- **isus203 / tecno-mt6768** - the KH7n (Spark 9 Pro) OrangeFox tree this is
  derived from, the TEE userspace, bootctrl, repartition tools, and the whole
  Transsion MT6768 recovery approach. https://github.com/tecno-mt6768
- **SebaUbuntu** - twrpdtgen and the generated TECNO-KI7 tree.
- **skkk** - the first unofficial TWRP for the Spark 10 Pro (XDA).
- TWRP / OrangeFox teams.
