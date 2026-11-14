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
| `TW_INCLUDE_NTFS_3G` / `TW_INCLUDE_FASTBOOTD` | true | false |
| `TW_EXCLUDE_TZDATA/LPTOOLS/LPDUMP/NANO` | false | true |
| Post-build slim | mandatory (`tools/slim_bootimg.py`) | backstop only (runs if image ever exceeds 32 MiB) |

Everything else — the crypto set (`TW_INCLUDE_CRYPTO*`, metadata partition,
Trustonic TEE relinks), fstab, boot header values, AVB, anti-rollback hack,
prebuilt kernel/dtb — is carried over unchanged.

## Build (CI)

`.github/workflows/twrp-build.yml` runs on every push to `twrp-12.1`:

1. sync minimal-manifest-twrp `twrp-12.1`
2. copy this repo into `device/tecno/KI7`
3. `lunch twrp_KI7-eng && mka recoveryimage`
4. assert the image fits the stock 32 MiB `boot_a` (slim backstop if not)
5. artifact `TWRP-KI7-r<run>-<ref>` containing `twrp-<version>-<date>-KI7.img`

Pushing a `v*` tag publishes a GitHub Release.

## Build (local)

```
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1
mkdir -p .repo/local_manifests
cp manifests/fox_12.1.xml .repo/local_manifests/tecno_ki7.xml
repo sync -c --no-clone-bundle --no-tags -j8
source build/envsetup.sh
lunch twrp_KI7-userdebug
mka recoveryimage
```

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

See README.md (Fox_12.1 branch) for the full flashing guide.

## Known limitations of this branch

- no fastbootd inside recovery (excluded for size) — flash `super` logical
  partitions from the stock side's fastbootd;
- no NTFS (exFAT/FAT still work via FUSE for external SDs);
- English-only UI;
- no OrangeFox features (themes, Fox addons, MIUI OTA handling).
