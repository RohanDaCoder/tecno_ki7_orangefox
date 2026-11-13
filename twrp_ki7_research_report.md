# TWRP port research — TECNO Spark 10 Pro (KI7)
**Compiled:** 2026-11-13 · All remote sources opened/verified on this date (via GitHub API/git/raw clone, curl; XDA & Reddit content captured via search-result extracts where direct fetch was blocked — marked "snippet").

**Scope:** P1 base/branch · P2 Transsion-MTK prior art · P3 recovery-as-boot + VAB + AVB · P4 FBE decryption · P5 32 MiB size budget · P6 GitHub Actions CI.

---

## 0. Recommendation (short)

**Use `minimal-manifest-twrp/platform_manifest_twrp_aosp`, branch `twrp-12.1`, plain TWRP — which your tree already supports as-is (`twrp_KI7.mk` + `AndroidProducts.mk` + `manifests/fox_12.1.xml` local-manifest instructions).**

Why (each point sourced below):
1. **OrangeFox R12.x is literally minimal-manifest `twrp-12.1` plus an OrangeFox layer.** The official `orangefox_sync.sh` (gitlab.com/OrangeFox/sync, v029 2026-09-13) repo-inits `https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git` with `TWRP_BRANCH="twrp-12.1"` for the 12.1 branch (script lines 53, 79). Your working, decrypting OrangeFox build therefore already proves the crypto stack of that exact base on this exact phone. Dropping the Fox layer removes size, not decryption capability.
2. **There is no `twrp-13.0` minimal-manifest branch.** Live branch list of `platform_manifest_twrp_aosp` (GitHub API, 2026-11-13): `twrp-11` (48a1ac92), `twrp-12.1` (6dc117d9, default, org pushed 2025-05-18), `twrp-14` (489c2928), `twrp-14.1` (cb31ddec). TeamWin's own `android_bootable_recovery` does have `android-13`/`android-14`/`android-14.1` branches (git ls-remote), but the minimal manifest jumped 12.1→14; 14.x is aimed at newer (GKI-era) devices, brings bigger ramdisks (bad for 32 MiB) and has no 4.19-prebuilt-MTK prior art. Community guidance (r/CustomROMsGuide, "Post 'omni' manifest twrp builds"): *"Since you are targeting Android 13.1, you must use the twrp-12.1 or twrp-14.1 (experimental)"* (snippet).
3. **A 12.1 base decrypts Android-13 ROM data on this SoC family.** Xiaomi Redmi 12 (`fire`, Helio G88/MT6769H, shipped Android 13/MIUI 14, platform `mt6768`, FBE+metadata) — its TWRP-12.1 tree README's feature checklist marks **"[X] decrypt /data"** (github.com/mahdi-salimi05/ofrp_device_xiaomi_fire, branch `android-12.1`; upstream referenced: redmi-fire-devs/twrp_device_xiaomi_fire). Your own device is the second data point (OrangeFox 12.1-based, FBE works — your ground truth).
4. **12.1 is where all MTK 4.19 prebuilt-kernel prior art lives** (KH7n, fire, CH6i, twrpdtgen-KI7 trees — all `TARGET_PREBUILT_KERNEL` + `--dtb`).
5. The branch README's *"FDE decryption is not presently supported in this branch"* note is irrelevant — KI7 is FBE.
6. The current `android-12.1` recovery branch builds **TWRP 3.7.1_12** (`variables.h:20 #define TW_MAIN_VERSION_STR "3.7.1_12"`, commit 5c3d206a, 2024-05-10) — i.e. official 3.7.1-class binaries come from this base; it is not stale.

Build target: `lunch twrp_KI7-eng` (or `-userdebug`), then **`mka recoveryimage`** — your `manifests/fox_12.1.xml` documents this for plain TWRP and notes the output `out/target/product/KI7/boot.img` *is* the recovery image (recovery-as-boot). The minimal-manifest README documents `mka bootimage` as the target for devices without a recovery partition — both work with `BOARD_USES_RECOVERY_AS_BOOT := true`; stay with what your tree documents.

---

## P1 — TWRP base & branch decision

### Q1 — Which base for an MT6768 device on an A13 ROM (API-30 launch)?
- Minimal-manifest branches (verified via API, 2026-11-13): **twrp-11, twrp-12.1, twrp-14, twrp-14.1 — no twrp-13.0.** https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp (branches endpoint). The org's READ_ME_FIRST (master) describes only "AOSP 11 & 12.1 branches, OmniROM 5.1–9.0, LineageOS 14.1" as the maintained set.
- TeamWin official tree branches (git ls-remote, 2026-11-13): android-9.0 … android-12.1, **android-13**, android-14, android-14.1 → an A13-era official base exists upstream, but was never productized as a minimal-manifest branch.
- TWRP 3.7.0 was the release that brought the Android-12 base: xda-developers.com, "TWRP 3.7.0 released, finally brings Android 12 support" (2022-10-12) https://www.xda-developers.com/twrp-3-7-0-release-android-12-support/ . The android-12.1 branch tip currently identifies as `3.7.1_12` (variables.h @ 5c3d206a, 2024-05-10). (3.7.2/3.7.3 release dates could not be verified this session — XDA/Reddit fetch-blocked; treat as unverified.)
- For contrast: the newest **official** TWRP for an MT6768-family device (Redmi Note 8 Pro / begonia, Helio G90T) is `twrp-3.7.0_9-0` — still on the Android-9 base (dl.twrp.me/begonia/, verified 2026-11-13). Modern MTK recoveries are community-built on the minimal manifest, not official builds.
- **12.1-based recovery decrypting A13 /data (fscrypt v2, ioctl FBE) — concrete MTK cases:**
  - Redmi 12 `fire` (Helio G88, A13/MIUI 14, mt6768): TWRP-12.1 tree, README checklist "[X] decrypt /data" — github.com/mahdi-salimi05/ofrp_device_xiaomi_fire @ `android-12.1` (tree also has `fox_12.1` OrangeFox branch).
  - TECNO Spark 10 Pro KI7 (this device): OrangeFox built on minimal twrp-12.1 via OrangeFox sync — FBE decryption working (your ground truth + repo README).
  - Negative reports for 12.1-on-A13 on MTK: none found in the sources opened this session (XDA/Hovatek bodies mostly unfetchable — marked as a research gap, not as evidence of absence).

### Q2 — Minimal manifest branches, lunch naming, makefile prefix
- README of `twrp-12.1` (raw, verbatim key lines): `repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1`; `cd <source>; export ALLOW_MISSING_DEPENDENCIES=true; . build/envsetup.sh; lunch twrp_<device>-eng`; build targets: recovery partition → `mka recoveryimage`; **boot image ramdisk → `mka bootimage`**; vendor_boot → `mka vendorbootimage`. Special notes: *"Device makefile in the device tree and dependencies file should use the 'twrp' prefix"* and *"FDE decryption is not presently supported in this branch."* The identical prefix/FDE notes appear on twrp-11/14/14.1 READMEs.
- Your tree already conforms: `AndroidProducts.mk` defines `twrp_KI7.mk` + `COMMON_LUNCH_CHOICES := twrp_KI7-user/-userdebug/-eng`; `manifests/fox_12.1.xml` documents the plain-TWRP flow (`lunch twrp_KI7-userdebug; mka recoveryimage`).
- Same pattern in the reference trees: `twrp_KH7n.mk` (tecno-mt6768/tecno_kh7n_recovery), `twrp_CH6i.mk` (twrp_device_tecno_CH6i), `twrp_fire-eng` (fire README).

### Q3 — Prebuilt 4.19 kernel handling (evidence from real MTK trees)
All four reference trees build with the stock prebuilt kernel and no kernel rebuild:
- `TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel` + `TARGET_PREBUILT_DTB := .../prebuilt/dtb(.img)` + `BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)` — used by twrpdtgen-KI7, KH7n (both recovery + orangefox), fire, and your tree.
- **Do NOT set `BOARD_INCLUDE_DTB_IN_BOOTIMG` with a prebuilt kernel on 12.1**: your BoardConfig comment documents the ninja failure ("missing and no known rule" for the kernel-built dtb.img); twrpdtgen and fire trees set it then explicitly unset it inside the `TARGET_FORCE_PREBUILT_KERNEL` guard (`BOARD_INCLUDE_DTB_IN_BOOTIMG :=` empty); KH7n's `BOARD_INCLUDE__DTB_IN_BOOTIMG` is a typo and therefore effectively unset — all four converge on "pass the dtb via `--dtb`".
- Boot header values used across these trees (identical to yours, from the stock header): header v2, base 0x40078000, pagesize 2048, kernel offset 0x00008000, ramdisk 0x07c08000, tags 0x0bc08000, second 0xbff88000, dtb offset 0x0bc08000, cmdline `bootopt=64S3,32N2,64N2 [buildvariant=user]`, `BOARD_KERNEL_IMAGE_NAME := Image` (KH7n uses `kernel`, fire uses `kernel` — the raw MTK image name).
- Separate `dtbo`: your tree ships `prebuilt/dtbo.img` (MTK DTBO container, magic d7b7ab1e) and `BOARD_DTBOIMG_PARTITION_SIZE := 8388608`; KH7n/fire trees leave dtbo alone in recovery builds (no `BOARD_PREBUILT_DTBOIMAGE` needed to *boot* recovery on these devices — dtbo_a/b are flashed stock and not modified by the recovery build).

---

## P2 — Transsion/MTK prior art

### Q4 — Existing trees found (all opened and read 2026-11-13)
| Tree | What it is | Why it matters |
|---|---|---|
| **github.com/tecno-mt6768/tecno_kh7n_recovery** (default branch) | Plain **TWRP 12.1** tree for TECNO Spark 9 Pro (KH7n), by isus203. `twrp_KH7n.mk`, full crypto flags, prebuilt kernel, MTK fstab (`KH7n-H6919DE-S-OP-230611V978`) | The direct ancestor of your tree; a *plain-TWRP* sibling already exists for the same platform/TEE |
| **github.com/mahdi-salimi05/ofrp_device_xiaomi_fire** @ `android-12.1` (also `fox_12.1`) | TWRP 12.1 tree for Xiaomi Redmi 12 (fire; Helio G88/MT6769H; **shipped A13**/MIUI 14; 1080x2460 like KI7) | Same silicon + A13 ROM + FBE; README checklist: decrypt /data ✓, slot switching ✓, backups ✓ |
| **github.com/twrpdtgen/android_device_tecno_TECNO-KI7** (default branch `vnd_ki7_v7510-user-12-SP1A.210812.016-817571-release-keys`, commit d461a4e, 2025-04-18; repo created 2023-07-31) | SebaUbuntu twrpdtgen-generated tree for **this device**, from the A12 `v7510` dump | Generated baseline; kernel/dtb blobs byte-identical to yours (per your README); lacks crypto flags and FBE fstab |
| github.com/tecno-mt6768/twrp_device_tecno_CH6i | TWRP tree (`twrp_CH6i.mk`) for TECNO CH6i (Camon family), same org | Confirms the org pattern generalizes across TECNO MT6768 models |
| github.com/tecno-mt6768/tecno_kh7n_orangefox, ..._shrp | OrangeFox/SHRP variants for KH7n | Multi-recovery maintenance pattern |
| github.com/tecno-mt6768/twrp_abtemplate | **A/B TWRP installer-zip template** (META-INF update-binary "TWRP A/B Installer Backend by osm0sis, Dees_Troy and topjohnwu" + magiskboot arm/arm64) | Ready-made both-slots installer approach (see P3) |
| github.com/Moto-Mediatek-Unified/android_device_motorola_penangf-twrp (+ local_manifests, device_motorola_vicky) | Moto G24-family (penangf), platform **mt6768** but GKI-style: boot header **v4**, `TARGET_NO_KERNEL`, `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT`, LZ4 ramdisk, `TW_LOAD_VENDOR_BOOT_MODULES`, PLATFORM_VERSION 14; crypto incl. `TW_USE_FSCRYPT_POLICY := 2`, `TW_FORCE_KEYMASTER_VER := true`. Releases: TWRP/SHRP/PBRP tags with 64 MB `vendor_boot.img` | Contrast model (vendor_boot-as-recovery) — **not** the template for KI7's header-v2 recovery-as-boot, but the only "unified MTK" org found |
| github.com/GakaLab/android_device_tecno_ki7 | KI7 tree that is actually a **copy of Xiaomi selene** (Redmi 10, Helio G88): `lineage_selene.mk`, `manifest_eos.xml`, LineageOS copyright headers | A LineageOS/e-OS effort for KI7, **not** a recovery tree — do not base TWRP on it |
| github.com/Shas45558/twrp_tree_mt6768 (branch `a14_lancelot`) | twrpdtgen tree for Redmi 9 (lancelot, mt6768 family) | Confirms lancelot/G80 devices share the mt6768 platform software |
| XDA: "guide to install recovery on the tecno spark 10 pro" (Nico 17, 2025-02-05; TWRP by **skkk**; attachment `10pro.img`, "32 MB") https://xdaforums.com/t/guide-to-install-recovery-on-the-tecno-spark-10-pro.4717108 | Unofficial TWRP for this exact device; flashing guide incl. slot dance | Proof a ≤32 MiB TWRP exists for KI7; reply #3 (2026-04-25) complains it "don't support dynamic partitions" — i.e. super handling suspect |
| Hovatek thread-47792 (2024-12-13) https://www.hovatek.com/forum/thread-47792.html | "Can i make a TWRP for my TECNO SPARK 10 PRO KI7? It has only BOOT.img" — answer: Hovatek Online TWRP Builder (hovatek.com/twrpbuilder/) with the boot.img | Confirms recovery-as-boot reality of KI7 in the Transsion modding community |

**Is there a maintained `device/mediatek/mt6768-common`?** No. The minimal-manifest-twrp org hosts only `platform_device_qcom_common` (Qualcomm; org repo list via API). The Transsion ecosystem (tecno-mt6768 org) inlines the shared bits per-device (Trustonic TEE userspace, `bootctrl` android.hardware.boot@1.2-mtkimpl, `mtk_plpath_utils`, sepolicy) and pulls `LineageOS/android_device_mediatek_sepolicy_vndr` + `android_hardware_mediatek` only for Lineage builds (their `local_manifest/local_manifest.xml`). Your tree already embeds everything needed — keep it self-contained.

### Q5 — SoC identity resolved
- Every relevant tree sets **`TARGET_BOARD_PLATFORM := mt6768`** — twrpdtgen-KI7, KH7n (both trees), your tree, fire (Redmi 12 **G88**), CH6i, penangf (Moto G24, G85-class), Shas45558/lancelot (Redmi 9, **G80**), GakaLab/selene (Redmi 10, **G88**).
- The Redmi 12 tree README spells it out: "Chipset: Mediatek **MT6769H Helio G88**" with `TARGET_BOARD_PLATFORM := mt6768`; your README: "Helio G88 (MT6769H, platform `mt6768`)".
- Conclusion: **Helio G80/G85/G88 (MT6769x) devices run on MT6768 platform software** (MSSI `alps-mp-t0`, kernel project `k6985v1.x` — the same kernel source family). Your dump (`ro.board.platform=t6768`, cmdline `tran_cpu_model=mt6769`, kernel `k6985v1.64`) matches exactly what these trees assume: **build for platform `mt6768`**, MTK T0/TSSI layout, kernel 4.19.191 prebuilt. No existing tree contradicts your facts.

---

## P3 — recovery-as-boot + virtual A/B specifics

### Q6 — Flashing/keeping TWRP on this class of device; init_boot
- **skkk's guide (XDA, this device, snippet)**: `fastboot flash boot twrp.img` → `fastboot reboot recovery` → in TWRP switch to slot b → *Advanced → "flash current TWRP"* → reboot, select slot a → restore the **original boot image to the other slot via SD** → system boots normally; **Vol+ at boot enters TWRP** (kept on the inactive slot). Also noted: you cannot flash Magisk from inside this TWRP; patch boot with the Magisk app and fastboot-flash it.
- **Your repo README (authoritative for KI7)**: custom recovery boot.img is recovery-only — flashing it to the active slot lands you in recovery on every boot until you restore stock. `fastboot boot` is usually blocked by the Transsion bootloader (`FAILED (remote: unknown command)`). Recommended: `dd`/fastboot to **boot_a only**, keep `stock_boot_a.img` forever, restore it to return to HiOS. OTAs overwrite boot — re-check `ro.boot.slot_suffix` after every OTA.
- **Installer zips for A/B/VAB**: `tecno-mt6768/twrp_abtemplate` ships the classic osm0sis/Dees_Troy/topjohnwu **A/B installer backend**: for `slot in _a _b` it dumps the current boot image, magiskboot-unpacks it, hexpatches the kernel (`want_initramfs`→`skip_initramfs`, `trip_initramfs`→`skip_initramfs`), swaps in the TWRP ramdisk cpio, repacks, and writes with `cat new-boot.img /dev/zero > $target$slot` — i.e. **zero-padded write to BOTH slots** (also clears stale AVB footers). This is the zip approach if you want "install from Magisk/recovery" distribution.
- **init_boot on non-GKI MTK (T0 MSSI)**: on KI7, `init_boot` (8 MiB) and `vendor_boot` are present but **unused by the header-v2 boot flow**; a recovery-as-boot image is self-contained in `boot` (your README: "vendor_boot/init_boot entries in twrp.flags exist for completeness — those partitions are unused on KI7 (header v2). Do not flash them."). External corroboration: the fire (Redmi 12, A13, 4.19) tree's `AB_OTA_PARTITIONS` lists no init_boot handling and recovery boots purely from boot; no tree in this ecosystem touches init_boot for recovery. Your own OrangeFox (A13, init_boot present) boots from boot_a — the documented case requested. **Caveat:** the KH7n lineage shows some Transsion GPTs are asymmetric — see Conflicts.

### Q7 — Virtual A/B support in TWRP 12.1
From the actual `android-12.1` source (TeamWin/android_bootable_recovery @ 5c3d206a, 2024-05-10):
- `recovery.cpp` reads `ro.virtual_ab.enabled` and on boot calls `CreateSnapshotPartitions()` (prints "Virtual A/B: snapshot partitions creation failed." on error).
- `install/snapshot_utils.cpp` implements `FinishPendingSnapshotMerges()` and `CreateSnapshotPartitions()` via `android::snapshot::SnapshotManager` (libsnapshot) — i.e. **TWRP 12.1 finishes pending VAB merges at recovery start and maps COW/snapshot devices before mounting /data**.
- There is **no** `TW_INCLUDE_SNAPUSERD` / `TW_INCLUDE_VIRTUAL_AB` board flag on this branch — VAB is runtime-auto-detected (`variables.h`: `tw_virtual_ab.enabled`; set from the system property). Your `device.mk` already inherits `virtual_ab_ota/compression.mk` and sets `ro.virtual_ab.enabled=true`.
- Real-world usage notes: your README — "TWRP 12.1 handles the COW device; avoid wiping `metadata` unless you know what you're doing" and "If an HiOS OTA was installed recently, let it boot several times so the Virtual A/B snapshot (COW) fully merges before overwriting boot_a." Community counterpoint (r/Android thread on 3.7.0, snippet): "Virtual A/B is supported. if you install something using twrp it only installs in one partition and you have conflicting system partitions" — treat VAB snapshot hygiene seriously; let merges finish before switching images.
- `adb remount` is not a TWRP concept (that's fastbootd); TWRP's own fastbootd (`TW_INCLUDE_FASTBOOTD`) is the route for flashing logical partitions — your slim build dropped fastbootd to save space, so flash super-logicals from fastbootd booted from the *stock* side or via `update_engine` sideload if you keep it.

### Q8 — AVB padding / vbmeta when flashing a raw image to the 32 MiB boot_a
- **Unlocked (orange) devices tolerate verification errors**: AOSP `external/avb` README (mirror: LineageOS/android_external_avw → android_external_avb @ lineage-20.0, "Locked and Unlocked mode"): *"…are fatal whereas in UNLOCKED state they are not. If the device is UNLOCKED pass `AVB_SLOT_VERIFY_FLAGS_ALLOW_VERIFICATION_ERROR`…"* (bootloaders do exactly this in orange state). The user-facing docs page (source.android.com/docs/security/features/verifiedboot/device-states) exists but is JS-rendered; content not extractable this session.
- **Device-level evidence**: skkk's TWRP boots on KI7 with no vbmeta step mentioned in the guide; your README: *"Flashing a vbmeta with `--flags 3` / `--disable-verity --disable-verification` is not required while the bootloader is unlocked and verified boot is orange"* and *"Orange state warning … is cosmetic."*
- **Padding mechanics**: a raw unpadded image leaves the *old* AVB footer/hash bytes at the tail of the partition (fastboot writes the file bytes; it does not zero-fill the remainder). The canonical A/B installer avoids stale-footer ambiguity by writing `cat image /dev/zero > partition` (twrp_abtemplate update-binary). Practical guidance for KI7: either ship the image zero-padded to 33,554,432 B, or flash then ignore the stale footer (orange state = non-fatal), or flash a `--flags 2/3` vbmeta once if you ever see verification-related refusals. Your CI already builds with `BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 2 --set_hashtree_disabled_flag` (harmless belt-and-braces).
- Cautionary report: XDA "[Question] Tecno Spark 10 pro(KI7) stuck bootloop" (2025-02-20, snippet) — user flashed `fastboot flash boot_a boot.img` plus a KI7 TWRP and bootlooped; cause not established from the snippet (wrong image/slot). Keep `stock_boot_a.img` + mtkclient/BROM as the rescue path (your README documents mtkclient works on the Helio G88 bootrom).

---

## P4 — FBE decryption (fscrypt v2 + metadata + Trustonic)

### Q9 — Known-good BoardConfig/device.mk/fstab combination (all evidenced in working trees)
**BoardConfig (KH7n recovery tree = plain TWRP 12.1, and your tree — identical set):**
```
TW_INCLUDE_CRYPTO               := true
TW_INCLUDE_CRYPTO_FBE           := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true
BOARD_USES_METADATA_PARTITION   := true
BOARD_ROOT_EXTRA_FOLDERS        += metadata tranfs
```
(TWRP source verifies these flags exist on android-12.1: `Android.mk` lines 339 & 358 consume `TW_INCLUDE_CRYPTO_FBE` and `TW_INCLUDE_FBE_METADATA_DECRYPT`; `partitionmanager.cpp` gates metadata-partition decryption on the latter.)

**Keymaster anti-rollback hack (KH7n, verbatim comment: "Hack to get keymaster to recognize the key files"):**
```
PLATFORM_VERSION        := 12.0.0
PLATFORM_SECURITY_PATCH := 2099-12-31
VENDOR_SECURITY_PATCH   := $(PLATFORM_SECURITY_PATCH)
```
(fire uses `PLATFORM_VERSION := 99.87.36` / patch `2127-12-31` — same trick, different values.)

**recovery.fstab (your tree and KH7n — keep exactly this shape):**
```
/dev/block/by-name/md_udc    /metadata   ext4  noatime,nosuid,nodev,discard   wait,check,formattable,first_stage_mount
/dev/block/by-name/userdata  /data       f2fs  noatime,...,inlinecrypt        wait,check,formattable,quota,latemount,resize,reservedsize=128m,checkpoint=fs,fileencryption=aes-256-xts:aes-256-cts:v2,keydirectory=/metadata/vold/metadata_encryption
```
Keep the full `fileencryption=...v2,keydirectory=...` string (TWRP parses it); keep `latemount` on /data; keep the `/metadata` (md_udc) entry mounted early. (fire's fstab adds `checkpoint_merge,fsync_mode=nobarrier` — optional.)

**device.mk (your tree — the TEE relink set that makes Trustonic keymaster 4.1 work in recovery):**
```
TARGET_RECOVERY_DEVICE_MODULES += libgatekeeper libgatekeeper_aidl libkeymaster41 libpuresoftkeymasterdevice
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += .../libgatekeeper.so .../libgatekeeper_aidl.so .../libkeymaster41.so .../libpuresoftkeymasterdevice.so
```
plus the full Trustonic userspace in `recovery/root/vendor/` (mcDriverDaemon, keymaster@4.1-service.trustonic, mcRegistry trustlets) and `init.recovery.trustonic.rc` service ordering — all already in your tree, inherited from KH7n.

**system.prop (your tree — keep):** `ro.crypto.volume.options=::v2`, `ro.crypto.volume.filenames_mode=aes-256-cts`, `ro.crypto.volume.metadata.method=dm-default-key`, `ro.crypto.dm_default_key.options_format.version=2`, `ro.vendor.keymaster_version=4.1`, `ro.hardware.gatekeeper/kmsetkey/paytrigger=trustonic`.

**Failure modes & fixes (documented in these sources):**
- Your README: *"FBE + metadata + Trustonic on an Android 12-based recovery is the hardest combination — it may take a few iterations (correct libs, correct order of services). Everything else (flash, backup, restore, wipe) works even without decryption."*
- Fix path when /data won't decrypt: refresh the TEE blobs from the live phone — `tools/vendor_refresh.sh` → tar → replace `recovery/root/vendor/` → rebuild (your README, "Refreshing the TEE blobs"). The tree ships KH7n's Trustonic stack (same platform/TEE); stale/foreign blobs are the classic "wrong password with correct PIN" cause on TEE devices.
- OrangeFox env for this device (vendorsetup.sh): `OF_FIX_DECRYPTION_ON_DATA_MEDIA=1`, `OF_DONT_PATCH_ENCRYPTED_DEVICE=1` (Fox-specific; plain TWRP doesn't need them).
- Newer-base extras seen on Moto penangf (A14-era, for reference): `TW_USE_FSCRYPT_POLICY := 2`, `TW_FORCE_KEYMASTER_VER := true`; fire adds `TW_PREPARE_DATA_MEDIA_EARLY := true`.

### Q10 — 12.1-based recovery vs A13 ROM (2025-secpatch fscrypt v2)
- No ioctl/fscrypt-v2 regression reports found in the sources opened: fire (A13, MIUI 14) decrypts on 12.1; your OrangeFox (12.1 base) decrypts a 2025-02-05-secpatch A13 HiOS right now. The ROM being A13 while recovery is A12.1-based is the **normal, working configuration** in this ecosystem (the recovery's fscrypt/keymaster userspace is self-contained in the ramdisk you ship).
- Related thread (could not open body — JS): Hovatek thread-49033 "Compatibility of OrangeFox Recovery built for Android 12…" (2025-09-27) — title alone shows this base-vs-ROM question is actively discussed; snippet mentions an online OrangeFox builder from an Android-11 boot.img.

---

## P5 — Size budget (32 MiB hard limit)

**The fixed costs (your dump):** kernel 10,759,203 B + dtb 123,221 B ≈ **10.88 MiB**, plus header/padding. Hard ceiling 33,554,432 B → **gzip ramdisk budget ≈ 20.4–20.7 MiB** (your CI uses LIMIT = 33,484,800 B).

**Measured data points:**
| Image | Size | Source |
|---|---|---|
| OrangeFox R12.x for KI7, full build | ramdisk ~88 MiB uncompressed / **~35.5 MiB gzipped** (does NOT fit) | your README + fox-build.yml comments |
| OrangeFox R12.x for KI7, after `slim_bootimg.py` | **~31.2 MiB total** (fits; CI-asserted ≤33,484,800) | your README ("The result lands around 31.2 MiB") + workflow |
| skkk's unofficial TWRP for KI7 | "32 MB" (XDA attachment `10pro.img`) | xdaforums thread 4717108 (2025-02-05) |
| Moto penangf TWRP (A14-era base, vendor_boot model) | 64 MB asset | Moto-Mediatek-Unified releases (expanded_assets) |
| begonia official TWRP 3.7.0_9 (A9 base) | n/a (page lists versions only) | dl.twrp.me/begonia/ |

**What the slim audit removed and kept (your README — the only measured before/after list found):** removed CJK font + 29 languages, nano/terminfo/gnused/gnutar, fastbootd, `update_engine_sideload`, MTP lib, NTFS stack, vibrator HALs, ASAN linker + UBSAN runtime, hwcomposer + libxml2, MTK pay-trigger factory stack, AOSP fallback UI images, and ICU (replaced by a freestanding stub — **4.3 MiB saved**, the single biggest cut); repacked with gzip -9, zopfli fallback. Kept: the whole FBE/Trustonic decryption stack, adb+sideload, bash, toybox, exFAT/FAT tools, logd, magiskboot + AVB/FRP tools.

**Implication for plain TWRP:** TWRP 12.1 is strictly smaller than OrangeFox R12.x at equal trims (no FOX_USE_* binaries — bash/nano/tar/sed/xz — no Fox theming/fonts/tools, no ICU-heavy Fox app stack). A trimmed plain-TWRP build should land at or below the 31.2 MiB OrangeFox figure — consistent with skkk's 32 MB build — but **"fits with margin" is not guaranteed by any published number I could verify**: no maintained 32-MiB-boot MTK device publishes plain minimal-TWRP-12.1 image sizes. Recommendation: build with the trim flags below, keep the CI size assert (`> 33,484,800 → fail`), and keep `slim_bootimg.py` as a backstop (it works on plain TWRP images too — it only prunes the ramdisk cpio).

**BoardConfig trims evidenced for this build** (flag existence verified in TWRP android-12.1 `Android.mk`; usage verified in KH7n/your trees):
```
TW_USE_TOOLBOX := true          # smaller than busybox set (KH7n, your tree; Android.mk:145/220)
TW_EXCLUDE_APEX := true         # Android.mk:76; KH7n + your tree
TW_EXCLUDE_PYTHON := true       # KH7n + your tree
TW_EXCLUDE_TWRPAPP := true      # KH7n + your tree
TW_EXCLUDE_TZDATA := true       # Android.mk:147/515 (KH7n keeps it false — flip it, saves tzdata)
TW_EXCLUDE_LPDUMP := true       # Android.mk:162 (KH7n keeps false; you don't need lpdump in recovery)
TW_EXCLUDE_LPTOOLS := true      # Android.mk:165 (same)
TW_EXTRA_LANGUAGES := false     # biggest font/language payload; your slim build already drops 29 langs + CJK
TW_INCLUDE_NTFS_3G := false     # your slim audit already removed the NTFS stack
TW_INCLUDE_FASTBOOTD := false   # removed in your slim build (flash logicals from stock-side fastbootd)
TW_INCLUDE_FB2PNG := false      # optional (fire sets true — costs a few hundred KB)
```

---

## P6 — GitHub Actions CI building TWRP 12.1 from the minimal manifest

**Example 1 — your own `fox-build.yml` (RohanDaCoder/tecno_ki7_orangefox @ Fox_12.1, `.github/workflows/fox-build.yml`):** the strongest reference because it already builds a 12.1-based recovery for KI7.
- Runner: **`ubuntu-22.04`, pinned on purpose** — comment: "AOSP 12.1 does not build on 24.04 (Python 3.12 / missing libtinfo5 / OpenSSL 3 breakage)"; timeout 330 min; ~25–30 min warm.
- Disk: `rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc /usr/share/swift /opt/hostedtoolcache …` + `docker image prune -af`; 10 GB swap on `/mnt`.
- ccache: **`CCACHE_DIR` must live inside the source tree** (Soong's nsjail mounts `/` read-only; only `$TOP`/`$TOP/out` writable — documented from a real failure); `CCACHE_COMPILERCHECK=content`, `CCACHE_SLOPPINESS=file_macro,locale,time_macros,include_file_ctime,include_file_mtime`, 8 GB cap (GitHub's 10 GB repo cache quota), per-commit key + prefix `restore-keys`, **save on failure** to warm the cache while iterating.
- Sync: OrangeFox sync script (which inits minimal twrp-12.1); device tree copied in; an upstream OrangeFox regression patch step (AID_MEDIA_RW include, recovery tip 6bd902d1, 2026-10-26).
- Build: `lunch twrp_KI7-eng` → `mka adbd bootimage`; slim step with LIMIT 33,484,800 B + zopfli retry; artifacts `OrangeFox-KI7-r<run_number>-<ref>.zip` (30-day retention); `v*` tags → GitHub Release with image + md5 + build_info.

**Example 2 — mahdi-salimi05/Action-TWRP-Builder (`.github/workflows/Recovery Build.yml`; fork lineage CaptainThrowback/Action-Recovery-Builder → azwhikaru → ZH-XiJun/mahdi):**
- Runner `ubuntu-24.04` + `rokibhasansagar/slimhub_actions` cleanup (conflict with Example 1's 22.04 note — 24.04 apparently workable with extra apt deps: libncurses, gperf, zulu JDK 11, etc.).
- `repo init --depth=1 -u minimal-manifest-twrp/platform_manifest_twrp_aosp -b twrp-12.1` (defaults), `repo sync -j$(nproc) --force-sync`, clones device (+optional common) tree, runs `scripts/convert.sh` on `twrp.dependencies` (branch-aware: twrp-11/twrp-12.1 → `twrp.dependencies`), 12 GB swap, `lunch <MAKEFILE_NAME>-eng && make <BUILD_TARGET>image` (BUILD_TARGET = boot | recovery | vendorboot), uploads via `softprops/action-gh-release`.
- Parameters (README table, ZH-XiJun fork): `MANIFEST_URL/BRANCH`, `DEVICE_TREE_URL/BRANCH`, `COMMON_TREE_URL/PATH`, `DEVICE_PATH`, `DEVICE_NAME`, `MAKEFILE_NAME` (twrp_<device>), `BUILD_TARGET`. ZH-XiJun release notes: 2022-07-04 "Updated to work with Android 12.1 AOSP minimal TWRP manifest"; 2022-07-08 "TWRP and TWRP-based 5.X ~ 12.X are ALL COMPILED SUCCESSFULLY".

**Example 3 — mahdi-salimi05/Action-OFRP-Builder (`.github/workflows/Recovery Build.yml`):** OrangeFox-specific variant — clones `gitlab.com/OrangeFox/sync`, sets up env via `OrangeFox/misc/scripts`, runner `ubuntu-20.04`, default manifest branch 11.0 (set 12.1 for KI7-class builds).

**Disk requirements:** OrangeFox wiki (wiki.orangefox.tech/dev/building): "You need at least **45GB** of disk space for the fox_12.1 branch" — plain minimal twrp-12.1 is smaller; your workflow's cleanup makes it fit the free runners. For heavy iteration, a community SSH-action with 125 GB storage for up to 6 h exists (gist: gist.github.com/lopestom/d85ce99bb244d308c5e681db31018626). XDA thread "Recovery Builder for TWRP, PBRP, OFRP and SHRP using GitHub Actions" (2024-12-15): xdaforums.com/t/4708087 (snippet) walks through forking such builders.

**For your TWRP branch:** clone `fox-build.yml` → swap the OrangeFox-sync steps for `repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1` + local manifest + `lunch twrp_KI7-eng` + `mka recoveryimage`; keep the pinned 22.04, the ccache block, the disk/swap steps and the size assert; rename artifacts `twrp-3.7.1_12-<date>-KI7.img` (matching the version string the branch produces).

---

## Conflicts & unverifiable items (explicit)

1. **boot_b size — CRITICAL, verify before any slot tricks.** Your brief: `boot_a = boot_b = 32 MiB`. Your repo README (same dump lineage, "verified on this device from the GPT"): **boot_b = 8 MiB, vendor_boot_b = 8 MiB** (asymmetric Transsion GPT), explicitly warning "a TWRP/OrangeFox image does NOT fit [boot_b] — never flash recovery here" and "the classic 'put TWRP on the inactive slot' trick is impossible on KI7." The skkk XDA guide's slot dance implies a usable slot b. Check on the phone: `adb shell su -c "blockdev --getsize64 /dev/block/by-name/boot_b"` (and boot_a) before flashing anything but boot_a.
2. **Kernel ramdisk decompression.** Brief: gzip ONLY (CONFIG-verified). Repo README: "only decompresses gzip/lz4/lzo (verified by extracting kallsyms)". Config wins — gzip-9/zopfli only (which is what the CI does anyway).
3. **Ubuntu 22.04 vs 24.04 for AOSP 12.1.** Your workflow: 24.04 broken (Python 3.12/libtinfo5/OpenSSL 3). mahdi's Action-TWRP-Builder: builds twrp-12.1 on ubuntu-24.04 with extra packages. Use 22.04 (pinned, proven for your tree).
4. **R12.0 vs R12.1 naming:** branch is `Fox_12.1`; OrangeFox's own build renames images `OrangeFox-R12.0_<date>-unofficial-KI7.img` (fox-build.yml comment) while the repo title says R12.1. Cosmetic.
5. **Unverified this session:** exact byte size of skkk's `10pro.img` ("32 MB" as displayed by XDA); TWRP 3.7.2/3.7.3 release dates and whether any official builds ship from the `android-13` branch; Hovatek thread bodies (thread-49033, -47792 body beyond the summary); contents of the XDA "Integrated Boot Image (KI7)" guide (title/snippet only: "Bypasses the typical MTK bootloop/Orange State conflicts", isottozu, 2026-10-29, xdaforums.com/t/4806823); no published size numbers for plain minimal-TWRP-12.1 images on comparable 32 MiB-boot MTK devices besides skkk's.
6. twrpdtgen-KI7 BoardConfig has `BOARD_BOOTIMAGE_PARTITION_SIZE := 33554430` (2 bytes short of 32 MiB — generator quirk); use your verified 33,554,432.

---

## Deliverable — BoardConfig.mk / device.mk flag set to adopt (copy-paste, commented)

Everything below is either already in your verified tree (keep) or evidenced in KH7n/fire trees + TWRP android-12.1 source. New/changed lines vs your current OrangeFox tree are marked **[TWRP-port]**.

```make
# --- identity / assert (keep) ---
DEVICE_PATH := device/tecno/KI7
ALLOW_MISSING_DEPENDENCIES := true
TARGET_OTA_ASSERT_DEVICE := TECNO-KI7,KI7,ki7

# --- architecture (keep your 64-bit-only decision) ---
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-2a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := cortex-a55
TARGET_BOARD_SUFFIX := _64
TARGET_USES_64_BIT_BINDER := true

# --- A/B, recovery-as-boot, VAB (keep; no VAB board flag exists on 12.1) ---
AB_OTA_UPDATER := true
TARGET_NO_RECOVERY := true
BOARD_USES_RECOVERY_AS_BOOT := true
BOARD_BUILD_SYSTEM_ROOT_IMAGE := false
BOARD_SUPPRESS_SECURE_ERASE := true
RECOVERY_SDCARD_ON_DATA := true

# --- platform (keep) ---
TARGET_BOARD_PLATFORM := mt6768
PRODUCT_PLATFORM := mt6768
BOARD_HAS_MTK_HARDWARE := true
BOARD_USES_MTK_HARDWARE := true
TARGET_USES_UEFI := true

# --- prebuilt kernel + dtb via --dtb (keep; do NOT set BOARD_INCLUDE_DTB_IN_BOOTIMG) ---
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
TARGET_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb
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
BOARD_MKBOOTIMG_ARGS += --base $(BOARD_KERNEL_BASE) --board $(BOARD_NAME) --pagesize $(BOARD_KERNEL_PAGESIZE)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET) --tags_offset $(BOARD_KERNEL_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --kernel_offset $(BOARD_KERNEL_OFFSET) --second_offset $(BOARD_KERNEL_SECOND_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET) --header_version $(BOARD_BOOTIMG_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)

# --- partitions (keep verified values; 32 MiB stock boot) ---
BOARD_FLASH_BLOCK_SIZE := 131072
BOARD_BOOTIMAGE_PARTITION_SIZE := 33554432
BOARD_DTBOIMG_PARTITION_SIZE := 8388608
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_SUPER_PARTITION_SIZE := 10522669056
BOARD_SUPER_PARTITION_GROUPS := main
BOARD_MAIN_SIZE := 10520571904
BOARD_MAIN_PARTITION_LIST := system vendor product system_ext
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_F2FS := true
TARGET_USERIMAGES_USE_EXT4 := true

# --- AVB (keep; harmless on unlocked orange device) ---
BOARD_AVB_ENABLE := true
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --set_hashtree_disabled_flag
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 2
BOARD_AVB_RECOVERY_ADD_HASH_FOOTER_ARGS += \
    --prop com.android.build.boot.os_version:$(PLATFORM_VERSION) \
    --prop com.android.build.boot.security_patch:$(PLATFORM_SECURITY_PATCH)

# --- keymaster anti-rollback hack (KH7n: "get keymaster to recognize the key files") ---
PLATFORM_VERSION := 12.0.0
PLATFORM_VERSION_LAST_STABLE := $(PLATFORM_VERSION)
PLATFORM_SECURITY_PATCH := 2099-12-31
VENDOR_SECURITY_PATCH := 2099-12-31

# --- metadata partition (FBE keydirectory) ---
BOARD_USES_METADATA_PARTITION := true
BOARD_ROOT_EXTRA_FOLDERS += metadata tranfs

# --- crypto: THE critical set (KH7n + your tree + fire) ---
TW_INCLUDE_CRYPTO := true
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true

# --- UI / device (keep verified) ---
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
TW_THEME := portrait_hdpi
TARGET_SCREEN_WIDTH := 1080
TARGET_SCREEN_HEIGHT := 2460
TARGET_SCREEN_DENSITY := 480
TW_BRIGHTNESS_PATH := /sys/class/leds/lcd-backlight/brightness
TARGET_RECOVERY_LCD_BACKLIGHT_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 3750
TW_DEFAULT_BRIGHTNESS := 1500
TW_INPUT_BLACKLIST := "hbtp_vm"
TW_STATUS_ICONS_ALIGN := center
TW_CUSTOM_CLOCK_POS := 660

# --- TWRP behavior (keep) ---
TW_DEFAULT_LANGUAGE := en_US    # [TWRP-port] KH7n uses ru; pick yours
TW_SCREEN_BLANK_ON_BOOT := true
TW_SKIP_ADDITIONAL_FSTAB := true
TW_SKIP_COMPATIBILITY_CHECK := true
TW_OZIP_DECRYPT_KEY := 0000
TW_NO_FASTBOOT_BOOT := true     # Transsion bootloader blocks `fastboot boot`
TW_NO_BIND_SYSTEM := true
TW_USE_TOOLBOX := true
TARGET_USES_MKE2FS := true
TW_BACKUP_EXCLUSIONS := /Files/backup
TARGET_USES_CUSTOM_LUN_FILE_PATH := /config/usb_gadget/g1/functions/mass_storage.usb0/lun.%d/file
TWRP_INCLUDE_LOGCAT := true
TARGET_USES_LOGD := true

# --- size trims for the 32 MiB budget --- [TWRP-port: flipped vs your Fox tree]
TW_EXTRA_LANGUAGES := false     # biggest save; slim audit already dropped 29 langs + CJK
TW_INCLUDE_NTFS_3G := false     # slim audit already removed NTFS
TW_INCLUDE_FUSE_EXFAT := true   # keep: external SD is exFAT/FAT
TW_INCLUDE_FASTBOOTD := false   # slim audit already removed it
TW_EXCLUDE_APEX := true
TW_EXCLUDE_PYTHON := true
TW_EXCLUDE_TWRPAPP := true
TW_EXCLUDE_TZDATA := true       # [TWRP-port] flip from false
TW_EXCLUDE_LPDUMP := true       # [TWRP-port] flip from false
TW_EXCLUDE_LPTOOLS := true      # [TWRP-port] flip from false
TW_EXCLUDE_BASH := true         # [TWRP-port] optional; bash ~1 MiB — only if you don't use the terminal
TW_EXCLUDE_MTP := true          # [TWRP-port] optional; slim audit removed the MTP lib

# --- keep for boot-image work (your integrated-boot/Magisk flows) ---
TW_INCLUDE_REPACKTOOLS := true
TW_INCLUDE_REPACK_TOOL := true
TW_INCLUDE_RESETPROP := true
TW_INCLUDE_LIBRESETPROP := true

# --- SELinux (keep) ---
TWHAVE_SELINUX := true
SEPOLICY_IGNORE_NEVERALLOWS := true
SELINUX_IGNORE_NEVERALLOWS := true
BOARD_SEPOLICY_DIRS += sepolicy/recovery

# --- recovery plumbing (keep) ---
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery/root/system/etc/recovery.fstab
TARGET_RECOVERY_INITRC := $(DEVICE_PATH)/recovery/root/init.recovery.mt6768.rc
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/system.prop
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += $(TARGET_OUT_SHARED_LIBRARIES)/libgatekeeper.so
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += $(TARGET_OUT_SHARED_LIBRARIES)/libgatekeeper_aidl.so
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += $(TARGET_OUT_SHARED_LIBRARIES)/libkeymaster41.so
TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += $(TARGET_OUT_SHARED_LIBRARIES)/libpuresoftkeymasterdevice.so
```

device.mk: keep your virtual_ab_ota/compression inherits, `PRODUCT_SHIPPING_API_LEVEL := 30`, bootctrl `android.hardware.boot@1.2-mtkimpl(.recovery)`, `mtk_plpath_utils`, and the whole TEE relink block verbatim (that's what makes Trustonic decrypt work). Remove OrangeFox-only bits (`FOX_*`/`OF_*` in vendorsetup.sh can be dropped for the TWRP branch).

---

## Deliverable — the 3 closest device trees + required diffs

### 1. github.com/tecno-mt6768/tecno_kh7n_recovery — TECNO Spark 9 Pro (KH7n), plain TWRP 12.1
The direct plain-TWRP sibling your tree was derived from (isus203 / tecno-mt6768). Diff needed vs your KI7 tree:
- Partition geometry: KH7n `BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296 #33554432` (repartitioned 96 MiB) → **use your verified 33554432**; super 9126805504 → **10522669056 / main 10520571904**.
- Panel: `TARGET_SCREEN_HEIGHT := 2408`, `TW_MAX_BRIGHTNESS := 2047`, `TW_CUSTOM_CLOCK_POS := 630` → your 2460 / 3750 / 660.
- `TW_DEFAULT_LANGUAGE := ru` → yours.
- KH7n builds with 2nd arch (arm) enabled → keep your 64-bit-only setup (your rationale: zero 32-bit libs on stock ramdisk).
- Keep: entire crypto block, AVB block, anti-rollback hack, fstab shape, TEE vendor (your tree already carries KH7n's Trustonic userspace + `tools/vendor_refresh.sh` to re-pull from a live KI7).
- `BOARD_INCLUDE__DTB_IN_BOOTIMG` typo: leave it out entirely (your `--dtb` approach is the fix).

### 2. github.com/mahdi-salimi05/ofrp_device_xiaomi_fire @ `android-12.1` — Xiaomi Redmi 12 (fire), Helio G88, shipped A13
Same silicon class, **Android 13 ROM, TWRP 12.1, decrypt /data confirmed working** — your best external validation of the base decision. Diffs:
- Boot: fire has 128 MiB boot (`BOARD_BOOTIMAGE_PARTITION_SIZE := 134217728`) and no size problem → keep your 32 MiB + slim/assert pipeline.
- `PLATFORM_VERSION := 99.87.36` / `PLATFORM_SECURITY_PATCH := 2127-12-31` (twrpdtgen's anti-rollback values) → prefer KH7n/yours (`12.0.0` / `2099-12-31`).
- fstab device paths: fire uses `/dev/block/platform/bootdevice/by-name/...`, adds `checkpoint_merge,fsync_mode=nobarrier` on /data, no `system_ext` in its dynamic list → keep your by-name + system_ext list (verified via lpdump).
- fire keeps `TW_EXTRA_LANGUAGES := true`, fastbootd, NTFS — the luxuries your 32 MiB budget can't afford.
- Consider adopting fire's `TW_PREPARE_DATA_MEDIA_EARLY := true` if you ever hit late-mount ordering issues.
- Upstream of this fork (per its README): github.com/redmi-fire-devs/twrp_device_xiaomi_fire.

### 3. github.com/twrpdtgen/android_device_tecno_TECNO-KI7 @ `vnd_ki7_v7510-user-12-SP1A.210812.016-817571-release-keys` (commit d461a4e, 2025-04-18)
Generated from an A12 dump of your exact device — useful as the "known-good generated baseline" to diff your hand-verified values against; its prebuilt kernel/dtb are byte-identical to yours. Diffs to bring it up to your level:
- Add the whole crypto block + `BOARD_USES_METADATA_PARTITION` + anti-rollback hack (generator adds none).
- Replace its placeholder super values (`9126805504 # TODO: Fix hardcoded value`) with your lpdump-verified ones.
- Fix `BOARD_BOOTIMAGE_PARTITION_SIZE := 33554430` → 33554432.
- Its fstab is the generator's basic version → use your recovery.fstab (md_udc metadata + FBE v2 fileencryption + system_ext).
- Drop the 2nd arch if you keep 64-bit-only; add your sepolicy/recovery, bootctrl, TEE relinks, vendor userspace.

(Honorable mentions: `tecno-mt6768/twrp_device_tecno_CH6i` — same org's Camon tree; `Moto-Mediatek-Unified/android_device_motorola_penangf-twrp` — mt6768 but GKI/vendor_boot model, useful only as contrast; avoid `GakaLab/android_device_tecno_ki7` — it is a selene/Lineage tree, not a recovery tree.)

---

## Source index (all opened 2026-11-13)
- https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp (+ branches API; README raw @ twrp-11/12.1/14/14.1) · https://github.com/minimal-manifest-twrp/READ_ME_FIRST · org repos API
- https://github.com/TeamWin/android_bootable_recovery (branches via git ls-remote; android-12.1 clone @ 5c3d206a 2024-05-10: variables.h, Android.mk, recovery.cpp, install/snapshot_utils.cpp)
- https://gitlab.com/OrangeFox/sync (orangefox_sync.sh v029) · https://wiki.orangefox.tech/dev/building · https://orangefox.download (+ /device/ki7 → 404)
- https://www.xda-developers.com/twrp-3-7-0-release-android-12-support/ (2022-10-12) · https://dl.twrp.me/begonia/ · https://twrp.me/Devices/TECNO/ → 404
- https://github.com/RohanDaCoder/tecno_ki7_orangefox @ Fox_12.1 (README, BoardConfig.mk, device.mk, system.prop, vendorsetup.sh, AndroidProducts.mk, twrp_KI7.mk, manifests/fox_12.1.xml, .github/workflows/fox-build.yml — cloned)
- https://github.com/tecno-mt6768 (org + tecno_kh7n_recovery, tecno_kh7n_orangefox, twrp_abtemplate, twrp_device_tecno_CH6i, local_manifest, build_scripts — cloned)
- https://github.com/mahdi-salimi05/ofrp_device_xiaomi_fire @ android-12.1 & fox_12.1 (cloned; README/BoardConfig/fstab)
- https://github.com/Moto-Mediatek-Unified/android_device_motorola_penangf-twrp (+ releases expanded_assets; local_manifests — cloned)
- https://github.com/twrpdtgen/android_device_tecno_TECNO-KI7 (cloned @ default branch vnd_ki7_v7510-user-12-…)
- https://github.com/GakaLab/android_device_tecno_ki7 (cloned) · https://github.com/Shas45558/twrp_tree_mt6768 (cloned)
- https://github.com/mahdi-salimi05/Action-TWRP-Builder & Action-OFRP-Builder & OrangeFox-Action-Builder (workflows cloned) · https://github.com/ZH-XiJun/Action-TWRP-Builder (README)
- https://xdaforums.com/t/guide-to-install-recovery-on-the-tecno-spark-10-pro.4717108 (2025-02-05; content via search extract) · https://xdaforums.com/tags/tecno-spark-10-pro (thread index incl. 4806823 integrated-boot guide, 2026-10-29; 2025-02-20 bootloop thread) · https://www.hovatek.com/forum/thread-47792.html (2024-12-13) · https://www.hovatek.com/forum/thread-49033.html (2025-09-27, title/snippet only)
- https://raw.githubusercontent.com/LineageOS/android_external_avb/lineage-20.0/README.md ("Locked and Unlocked mode") · https://source.android.com/docs/security/features/verifiedboot/device-states (JS-rendered; content not extracted)
- https://www.reddit.com/r/CustomROMsGuide/comments/1r76nv9/post_omni_manifest_twrp_builds (snippet) · https://www.reddit.com/r/Android/comments/y3mbeu/twrp_370_released_with_android_12_support (snippet) · https://gist.github.com/lopestom/d85ce99bb244d308c5e681db31018626 (snippet) · https://xdaforums.com/t/recovery-builder-for-twrp-pbrp-ofrp-and-shrp-using-github-actions.4708087 (snippet)
- https://github.com/twiks228/tecno-spark-10-pro-gsi-guide · https://github.com/AhmadMorningstar/Tecno-Spark-10-Root-Guide
