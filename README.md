# TWRP 12.1 for TECNO Spark 10 Pro (KI7)

**Maintainer:** [RohanDaCoder](https://github.com/RohanDaCoder) (AL Zami Rohan)

[![Build](https://github.com/RohanDaCoder/tecno_ki7_orangefox/actions/workflows/twrp-build.yml/badge.svg?branch=twrp-12.1)](https://github.com/RohanDaCoder/tecno_ki7_orangefox/actions/workflows/twrp-build.yml)
[![Releases](https://img.shields.io/github/v/release/RohanDaCoder/tecno_ki7_orangefox?include_prereleases&label=release)](https://github.com/RohanDaCoder/tecno_ki7_orangefox/releases)

Ready-to-build **TWRP 3.7.1_12 (unofficial)** device tree for the Tecno Spark
10 Pro (codename **KI7**, board `CY-KI7-V7510`).

The `twrp-12.1` branch is a **pure TWRP tree**: it started as a copy of the
OrangeFox port in this same repo, but every OrangeFox layer, OrangeFox build
variable and post-build slimming tool has been removed. Plain TWRP fits the
stock 32 MiB `boot_a` partition with no post-build surgery; the OrangeFox
ramdisk never did. The historical OrangeFox port stays on the `Fox_12.1`
branch.

Most board values were verified against a **live dump** of a rooted KI7
(HiOS `KI7-V7510AACDGHJKLMN-T-GL-250218V5302`, Feb 2025 firmware): boot image
header, partition table, super layout (`lpdump`), stock fstab, display, and
the kernel blob. A device-side re-verification round is in progress — items
marked **RE-VERIFY** below are being confirmed on the live phone and this
table will be corrected if the measurement disagrees.

Research basis: `twrp_ki7_research_report.md`. Branch-specific notes: `TWRP.md`.

## Automated builds (GitHub Actions)

`.github/workflows/twrp-build.yml` builds TWRP on every push to `twrp-12.1`
(no local setup needed):

- **Normal commits**: the recovery image is stored as a **workflow artifact**
  (repo → *Actions* → the run → *Artifacts*, kept for 30 days).
- **Releases**: push a tag that starts with `v` and CI cuts a full **GitHub
  Release** with the image, its md5 and a bundle zip:

  ```bash
  git tag v1.0-twrp
  git push origin v1.0-twrp
  ```

Expect ~1.5-3 h per cold build on the free public-repo runners
(ccache-warmed rebuilds are much faster).

## Device

Basic | Spec Sheet
-----:|:------------------------
SoC | MediaTek Helio G88 (MT6769H, platform `mt6768`) — RE-VERIFY via SoC props
CPU | 2x Cortex-A75 @2.0GHz + 6x Cortex-A55 (armv8.2)
GPU | Mali-G52 MC2
Kernel | 4.19.191 (stock, prebuilt - included in `prebuilt/`) — RE-VERIFY via `uname`
OS | Android 13 system / Android 12 vendor (TSSI)
Display | 6.8" 1080x2460 @ density 480, max backlight 3750
Battery | 5000 mAh
Slots | A/B, **Virtual A/B + compression** (`ro.virtual_ab.enabled=true`)
Crypto | **FBE** + metadata encryption (keydirectory on `md_udc`), Trustonic TEE — RE-VERIFY
Boot image | header **v2**, board name `CY-KI7-V7510`, page 2048, base 0x40078000, ramdisk 0x07c08000, tags 0x0bc08000, dtb 0x0bc08000

### Partition layout (from `lpdump` / `/proc/partitions` — re-verification in progress)

Partition | Size | Notes
---:|---:|---
boot_a | 33,554,432 (32 MiB) | **recovery-as-boot**, flash target: kernel + dual-purpose ramdisk (normal init + `system/bin/recovery`)
boot_b | **RE-VERIFY: 8 MiB (GPT dump) vs 32 MiB (live report)** | whatever the truth: never flash recovery here without measuring again first
vendor_boot_a | 67,108,864 (64 MiB) | **unused** (boot header v2) - merge candidate for repartition
vendor_boot_b | 8,388,608 (8 MiB) | **unused** (boot header v2)
init_boot_a / _b | 8,388,608 (8 MiB) | **unused** (boot header v2)
dtbo_a / _b | 8,388,608 (8 MiB) | MTK DTBO container (magic `d7b7ab1e`)
super | 10,522,669,056 | group `main`, max 10,520,571,904: system, vendor, product, system_ext (+cow)
userdata | f2fs, FBE | `fileencryption=aes-256-xts:aes-256-cts:v2`, keydirectory `/metadata/vold/metadata_encryption`
metadata | `md_udc` | FBE metadata/keydirectory
preloader | `mmcblk0boot0/1` | 4 MiB each

There is **no dedicated recovery partition** — RE-VERIFY (by-name listing +
boot ramdisk unpack). The stock `boot.img` ramdisk contains both the normal
boot init and the HiOS recovery binary (`system/bin/recovery`,
`system/etc/recovery.fstab`, `system/lib64/librecovery_ui.so`). The bootloader
picks recovery vs normal via `androidboot.force_normal_boot`.

## Tree layout

```
tecno_ki7_orangefox/   # clone as device/tecno/KI7
├── .github/workflows/twrp-build.yml                # CI: artifacts on push, release on v* tags
├── manifests/twrp_12.1.xml                          # local_manifest for repo sync
├── AndroidProducts.mk / twrp_KI7.mk / Android.mk   # lunch: twrp_KI7-userdebug
├── BoardConfig.mk                                   # all verified KI7 values
├── device.mk                                        # Virtual A/B, bootctrl, TEE relinks, fastbootd
├── system.prop                                      # recovery props (crypto/TEE/USB)
├── prebuilt/                                         # kernel (gzip Image), dtb, dtbo.img
│                                                    #   from the live dump - byte-identical
│                                                    #   to the twrpdtgen A12 firmware dump
├── recovery/root/
│   ├── first_stage_ramdisk/fstab.mt6768             # stock KI7 first-stage fstab
│   ├── init.recovery.mt6768.rc                      # MTK init + Trustonic TEE services
│   ├── init.recovery.tee.rc / init.recovery.trustonic.rc
│   ├── init.recovery.usb.rc / ueventd.mt6768.rc
│   ├── system/etc/recovery.fstab + twrp.flags       # KI7 by-name verified
│   ├── system/lib64/                                # keymaster/gatekeeper relink libs
│   └── vendor/                                      # full Trustonic TEE userspace
│       ├── bin/          (mcDriverDaemon, keymaster@4.1-service.trustonic, ...)
│       ├── app/mcRegistry/  (trustlets .drbin/.tlbin/.tabin)
│       ├── lib64/ + lib64/hw/  (keymaster, gatekeeper, hwcomposer.mt6768)
│       └── thh/ta/       (trusted apps)
├── bootctrl/             # android.hardware.boot@1.2-mtkimpl (source)
├── mtk_plpath_utils/     # preloader raw-link helper (source)
├── avb/boot_pubkey.pem   # Transsion MT6768 AVB key (from the KH7n tree)
├── sepolicy/recovery/    # recovery.te allow rules
├── tools/vendor_refresh.sh  # pull YOUR /vendor TEE blobs from the live phone
└── twrp_ki7_research_report.md  # the research that picked this base
```

`recovery/root/vendor` is taken from the KH7n (Spark 9 Pro) tree - same platform,
same Trustonic TEE. If decryption misbehaves, run `tools/vendor_refresh.sh` on the
phone and drop your own blobs in (see below).

## Building

Requirements: Linux x86_64 (Ubuntu 20.04/22.04), 16 GB+ RAM, ~250 GB disk,
standard Android build prerequisites (`repo`, `git`, build-essential, etc.).

```bash
mkdir ~/twrp && cd ~/twrp
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1

# pull in the KI7 device tree:
mkdir -p .repo/local_manifests
curl -o .repo/local_manifests/tecno_ki7.xml \
  https://raw.githubusercontent.com/RohanDaCoder/tecno_ki7_orangefox/twrp-12.1/manifests/twrp_12.1.xml

repo sync -c --no-clone-bundle --no-tags -j8

source build/envsetup.sh
lunch twrp_KI7-userdebug
mka adbd bootimage -j$(nproc)
```

**`mka adbd bootimage`, NOT `mka recoveryimage`.** KI7 is recovery-as-boot
(`BOARD_USES_RECOVERY_AS_BOOT := true`), and on this build system (TeamWin
android-12.1 `build/make`) the `recoveryimage` target is deliberately empty
for such boards — building it yields `ninja: no work to do`, a "successful"
build with zero compilations and no image. The `bootimage` target produces
`out/target/product/KI7/boot.img` from the recovery ramdisk (AVB-padded to
exactly 33,554,432 bytes = the stock 32 MiB boot_a; flashable as-is).

Or just let [GitHub Actions](#automated-builds-github-actions) build it.

### The 32 MiB boot_a limit (READ THIS)

The stock `boot` partition is only **32 MiB**. Plain TWRP with the
BoardConfig size trims fits it:

- single language / no CJK font stack (`TW_EXTRA_LANGUAGES := false`)
- no NTFS-3G (exFAT/FAT stay, via FUSE)
- no tzdata / lptools / lpdump / nano
- everything decryption- and flashing-related **stays in**

**fastbootd is deliberately kept in** (`TW_INCLUDE_FASTBOOTD := true` — see
TWRP.md): while this recovery occupies `boot_a`, its fastbootd is the only
route to flash the `super` logical partitions.

There is **NO post-build slim/repack tooling on this branch** — the old
OrangeFox slimming pipeline (`tools/slim_bootimg.py`) is exactly how
fastbootd was lost the first time, and it has been deleted. CI hard-fails
if the image ever exceeds 33,554,432 bytes; the trimming decision then
belongs in `BoardConfig.mk`, not in CI surgery.

The stock kernel only decompresses **gzip/lz4/lzo** initramfs (no xz/zstd -
verified by extracting kallsyms from the prebuilt kernel), so the build
stays with the default gzip ramdisk.

## Flashing

**First, make a safety net** (you have root):

```bash
adb shell su -c "dd if=/dev/block/by-name/boot_a of=/sdcard/stock_boot_a.img"
adb pull /sdcard/stock_boot_a.img   # keep this forever
```

Your rescue options if anything goes wrong: `mtkclient` (Helio G88 bootrom is
exploitable - can flash any partition via BROM mode), SP Flash Tool with the stock
ROM from needrom.com, or fastboot. Keep the dumped `boot.img`, `dtbo.img`,
`vbmeta*.img` and `ins_preloader.img` somewhere safe.

### How recovery works on KI7 (read this - it is NOT the usual slot dance)

A TWRP `boot.img` contains a recovery-only ramdisk. The stock boot image is
dual-purpose (normal boot + recovery); a custom recovery image is not: flash
it to the active slot and every boot lands in recovery until you reflash
stock.

**boot_b size is currently under re-verification** (GPT dump said 8 MiB; a
live check reported 32 MiB). Until that is settled, treat the classic "put
TWRP on the inactive slot" trick as unavailable - flash TWRP to `boot_a`
when you need it, reflash the stock boot image afterwards. Your active slot
is `_a` (check: `getprop ro.boot.slot_suffix`) - re-check after every OTA,
because an OTA that flips the active slot changes the whole picture.

### Option A - flash TWRP to boot_a (the default)

Keep a copy of the stock boot image around - forever (see the safety net
above). Flash TWRP:

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

### fastbootd (logical partitions)

With this recovery in `boot_a`, `adb reboot fastbootd` boots the same ramdisk
into fastbootd - the only route to flash `super` logical partitions
(system / vendor / product / system_ext) while the recovery occupies `boot_a`:

```
fastboot flash system system.img      # logical partitions via fastbootd
fastboot reboot                        # back to recovery (recovery-as-boot)
```

### If you flashed TWRP to boot_b by accident

If boot_b really is 8 MiB, the image was truncated there and slot B is not
bootable this way - do not switch the active slot to `b` afterwards, and
re-check `ro.boot.slot_suffix` before the next OTA. A future OTA (or
mtkclient) can rewrite `boot_b` properly. (If boot_b turns out to be a full
32 MiB after re-verification, this section will be updated.)

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

- English-only UI; no NTFS (exFAT/FAT still work via FUSE for external SDs);
  no OrangeFox features (themes, Fox addons) — this is plain TWRP.
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
- TWRP team.
