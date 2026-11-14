# TWRP 12.1 for TECNO Spark 10 Pro (KI7) — `twrp-12.1` branch

Plain TWRP port of the Fox_12.1 device tree. Same verified device facts
(prebuilt stock 4.19 kernel, recovery-as-boot, virtual A/B, FBE + Trustonic
keymaster 4.1) — the OrangeFox layer is simply not applied, because the
OrangeFox ramdisk cannot fit the stock 32 MiB `boot_a` even after aggressive
post-build slimming, while plain TWRP does.

Research basis for the branch decision: `twrp_ki7_research_report.md`.

## What changed vs `Fox_12.1`

| Area | Fox_12.1 | twrp-12.1 |
|---|---|---|
| Manifest | OrangeFox sync (minimal twrp-12.1 + Fox layer) | minimal-manifest-twrp `twrp-12.1` directly |
| `BOARD_BOOTIMAGE_PARTITION_SIZE` | 100663296 (96 MiB repartition, README Option C) | **33554432 (stock 32 MiB boot_a)** |
| `TW_EXTRA_LANGUAGES` | true (CJK font stack, 29 languages) | false (en_US only) |
| `TW_INCLUDE_NTFS_3G` | true | false |
| `TW_INCLUDE_FASTBOOTD` | true | **true (kept — restored 2026-11-14)** |
| `TW_EXCLUDE_TZDATA/LPTOOLS/LPDUMP/NANO` | false | true |
| Post-build slim | mandatory (`tools/slim_bootimg.py` cut mode) | **none — slim tooling deleted; CI hard-fails if over 32 MiB** |

Everything else — the crypto set (`TW_INCLUDE_CRYPTO*`, metadata partition,
Trustonic TEE relinks), fstab, boot header values, AVB, anti-rollback hack,
prebuilt kernel/dtb — is carried over unchanged.

## Build (CI)

`.github/workflows/twrp-build.yml` runs on every push to `twrp-12.1`:

1. sync minimal-manifest-twrp `twrp-12.1`
2. copy this repo into `device/tecno/KI7`
3. `lunch twrp_KI7-eng && mka adbd bootimage` (recovery-as-boot: the
   `recoveryimage` target is empty on such boards — building it is a no-op
   that yields "ninja: no work to do" and no image)
4. hard-fail if the image does not fit the stock 32 MiB `boot_a` (no slim/repack tooling — it is deleted on this branch)
5. artifact `TWRP-KI7-r<run>-<ref>` containing `twrp-<version>-<date>-KI7.img`

Pushing a `v*` tag publishes a GitHub Release.

## Fastbootd

**Included on this branch** (`TW_INCLUDE_FASTBOOTD := true` in BoardConfig.mk
plus `fastbootd` + the mock fastboot HAL in `device.mk` PRODUCT_PACKAGES;
restored 2026-11-14 after the first port draft cut it for size).

`adb reboot fastbootd` — from HiOS with the stock boot image, or from inside
this recovery — reboots into this same `boot_a` ramdisk in fastbootd mode,
exactly like the stock image does (verified on the live device). While this
recovery occupies `boot_a` the stock side is unreachable, so this ramdisk's
fastbootd is **the only route to flash `super` logical partitions**
(system / vendor / product / system_ext):

```
fastboot flash system system.img      # logical partitions via fastbootd
fastboot reboot                        # back to recovery (recovery-as-boot)
```

There is therefore NO post-build slim/repack tooling on this branch —
`tools/slim_bootimg.py` (and the ICU stub) were deleted outright: losing
fastbootd is exactly how the slimmed OrangeFox build ended up without it,
so there is no post-build surgery at all. CI hard-fails if the image
ever exceeds the stock 32 MiB `boot_a`.

## Build (local)

```
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1
mkdir -p .repo/local_manifests
cp manifests/twrp_12.1.xml .repo/local_manifests/tecno_ki7.xml
repo sync -c --no-clone-bundle --no-tags -j8
source build/envsetup.sh
lunch twrp_KI7-userdebug
mka adbd bootimage
```

**Why `bootimage` and not `recoveryimage`:** KI7 is recovery-as-boot
(`BOARD_USES_RECOVERY_AS_BOOT := true`). In this build system (TeamWin
android-12.1 `build/make`) `INSTALLED_RECOVERYIMAGE_TARGET` is left empty on
purpose for such boards, so `mka recoveryimage` is a phony target with zero
dependencies — `ninja: no work to do`, "build completed successfully", and no
image at all (that is exactly how the first CI run of this branch failed).
`bootimage` maps to `INSTALLED_BOOTIMAGE_TARGET` (= `boot.img`, built from the
recovery ramdisk). `adbd` is named explicitly too — belt and braces, the same
incantation the OrangeFox flow uses.

Output: `out/target/product/KI7/boot.img` (recovery-as-boot; AVB-padded to
exactly 33,554,432 bytes = zero-padded, flashable as-is).

## Flashing

Identical rules to the OrangeFox build — KI7 has no dedicated recovery
partition:

- keep `stock_boot_a.img` forever (rescue path);
- write to `boot_a` only (`fastboot flash boot_a` / `dd`);
- while the recovery image is installed in `boot_a`, every boot lands in
  recovery — restore the stock image to return to HiOS;
- `fastboot boot` is blocked by the Transsion bootloader;
- OTAs overwrite `boot_a` — re-check the active slot after every OTA.

See README.md (this branch) for the full flashing guide.

## Known limitations of this branch

- no NTFS (exFAT/FAT still work via FUSE for external SDs);
- English-only UI;
- no OrangeFox features (themes, Fox addons, MIUI OTA handling).
