#!/usr/bin/env python3
"""slim_bootimg.py -- surgical OrangeFox boot.img slimming for TECNO KI7.

Goal: fit the recovery into the STOCK 32 MiB boot_a (limit 33,484,800 bytes)
without breaking decryption or the features this device actually needs.

Hard constraint discovered the hard way: the stock prebuilt kernel only
decompresses gzip / lz4 / lzo initramfs (kallsyms extracted from the kernel
blob has gunzip + unlz4 + lzo1x_decompress_safe, NO unxz/unzstd). So xz/zstd
ramdisks would not boot; the levers are CONTENT CUTS + gzip -9.

Pipeline:
  1. parse the header-v2 boot image produced by the build (96 MiB padded)
  2. decompress the gzip ramdisk cpio
  3. drop entries on the cut list (files + whole trees)
  4. regenerate OrangeFox's ramdisk-files.txt / ramdisk-files.sha256sum so the
     built-in ramdisk integrity check stays consistent
  5. optionally swap libandroidicu.so for tools/libandroidicu-stub-aarch64.so
     and drop libicuuc.so + libicui18n.so
  6. recompress the cpio with gzip -9 (or zopfli as a fallback)
  7. repack the boot image with the original header fields + recomputed id

Everything else (kernel, dtb, cmdline, addresses, page size, uid/gid/modes of
kept files) is preserved byte-identical: kept cpio entries are re-emitted from
their original raw byte slices.

=== AUDIT TRAIL: every cut and why it is safe =============================

Verified with: ELF DT_NEEDED graph (readelf/nm), symbol import counts per
dependency, rc-file service scan, string references in the recovery binary,
and shell-script greps (foxstart.sh + FFiles tool zips).

DELIBERATELY KEPT despite looking removable:
  sbin/bash           /sbin/sh AND /sbin/ash symlink to it; foxstart.sh runs
                      through it (statically linked, no deps)
  sbin/magiskboot     referenced by FFiles/OF_avb10.zip, FFiles/OF_verity_crypt.zip
                      and OF_avb20.sh - the AVB / dm-verity survival tools
  system/bin/minadbd  TWRP sideload mode (adb sideload of zips)
  system/bin/pigz     TWRP backup gzip acceleration
  system/bin/{charger,watchdogd,bootctl,resetprop,simg2img,unzip,getevent}
                      rc services / scripts / debugging tools
  android.hardware.{boot,health}@*-service    started by init.recovery.mt6768.rc
  vold_prepare_subdirs, fscryptpolicyget + libincfs.so   FBE decryption helpers
  system/lib64/liblzma.so                     needed by libunwindstack.so
  exfat / fat tools                           external SD (>32 GiB is exFAT)
  vendor/** + mcRegistry + thh/ta             the whole Trustonic TEE decryption
                      stack (keymaster/gatekeeper TAs) - untouchable
  keystore2 + libsqlite (+ ICU stub)          FBE decryption chain:
                      libtar(fscrypt) -> keystore2 -> sqlite -> libandroidicu
  ICU stub: libsqlite imports 21 u_*_android symbols from libandroidicu ONLY
  for collation; keystore2 uses binary collation. The stub makes ucol_open()
  return a dummy handle with U_ZERO_ERROR so sqlite3_open() keeps succeeding;
  ucol_strcoll returns 0 (affects only COLLATE ICU queries - never issued).
  Source: tools/icu_stub.c (freestanding, no libc).

CUTS (grouped, with the evidence):
  twres/fonts/wqy-microhei.ttf (4.9 MiB)
      only referenced by twres/languages/zh_CN.xml (fontoverride) - and the
      zh/ja/ko language files are cut with it
  twres/languages/*.xml except en/bn_BD/hi_IN (2.3 MiB)
      device markets; OrangeFox falls back to en.xml (default, referenced
      by the recovery binary)
  system/etc/terminfo + FFiles/nano (3.8 MiB)
      terminal escape tables + nano editor; /sbin/sh is bash, works without
  sbin/gnused + sbin/gnutar (1.6 MiB)
      never referenced by name in any script; toybox sed/tar cover PATH calls
  res/images/** (3.2 MiB)
      AOSP classic-recovery UI PNGs; OrangeFox draws its themed UI from
      twres/ and never reads res/ (no string references in the binary)
  vendor/bin/paytrigger_test + paytrigger HAL service + libs + manifest
      Mediatek factory pay-trigger test stack; zero references in the
      recovery binary; removed from the device tree + rc files in the same
      commit that introduced this script
  system/bin/{update_engine_sideload,fastbootd,zip,avbctl} + sbin/zip
      update_engine_sideload: A/B payload.bin sideload path (OrangeFox's own
      installer handles normal zips); fastbootd: userspace fastboot daemon;
      zip CLIs: installer uses libziparchive in-process
  system/bin/{snapuserd,e2fsck}
      dead duplicates: init's switch_root() moves first_stage_ramdisk/* over
      / at first-stage init, so those copies replace these files at boot
  vendor/lib64/hw/hwcomposer.mt6768.so + system/lib64/libxml2.so
      hwcomposer: no composer service binary exists in the ramdisk and no
      ELF NEEDs it -> never loaded; libxml2's only user was hwcomposer
  system/bin/linker_asan64 (1.7 MiB) + libclang_rt.ubsan (0.75 MiB)
      ASAN runtime linker / UBSan runtime - no sanitized binaries exist in
      the ramdisk
  system/lib64/libncurses.so       only user was nano (cut); bash is static
  system/lib64/libtwrpmtp-ffs.so   MTP ffs lib; zero refs anywhere
  libntfs-3g + mount/mkfs/fsck.ntfs  NTFS stack (exFAT + FAT kept)
  vibrator HAL .so x9, fastboot@1.1 HAL, health.storage libs, libnl,
  libservices, libcppbor, libtinyalsa, libdmabufheap, libnos_*, libnetd_client
  (libc dlopens it lazily and falls back), libhardware_legacy,
  android.hidl.token utils, lptools, modprobe, bzip2, bc, xz/lzma CLIs,
  FFiles/ps, flash/dump/erase_image + libflashutils/libbmlutils/libmmcutils,
  twrp, ozip_decrypt, openaes, bu, zipinfo, ziptool
      orphans of the ELF dependency graph from every root (recovery, init,
      adbd, keystore2, magiskboot, toybox, rc-started services, the whole
      vendor/ TEE stack)
  theme fonts except InterDisplay x2 + Roboto x2 (1.2 MiB)
      OrangeFox 12.1 default UI fonts + fallback; the exotic font choices go
  ramdisk-files.txt / .sha256sum
      regenerated from the final entry set (formats match the originals)

Usage:
  slim_bootimg.py IN_IMG OUT_IMG [--icu-stub STUB_SO] [--zopfli BIN] \
      [--zopfli-iterations N] [--report-only] [--save-cpio PATH] [--no-tier2] \
      [--no-cut]

--no-cut mode (the twrp-12.1 branch CI backstop): NOTHING is removed or
rewritten - every cpio entry is re-emitted byte-identical (raw slices), the
Fox ramdisk manifests stay untouched, and only the ramdisk compression
(gzip -9, zopfli fallback) plus the boot image header are regenerated.
Reason: fastbootd is a hard requirement on the twrp-12.1 branch - `adb
reboot fastbootd` must boot this ramdisk into fastbootd, and while the
recovery occupies boot_a it is the only route to flash super/logical
partitions. The cut lists of the OrangeFox build would silently remove
system/bin/fastbootd and its HAL, so that mode must never run there.
"""
import argparse
import gzip
import hashlib
import os
import re
import struct
import sys

# ----------------------------------------------------------------------------
# cut list
# ----------------------------------------------------------------------------
# Tier 1 - locale/cosmetic/factory junk (no recovery feature loss):
TIER1_FILES = [
    'twres/fonts/wqy-microhei.ttf',
    'twres/fonts/wqy-microhei_README.txt',
    'system/bin/keystore_cli_v2',
]
TIER1_TREES = [
    'system/etc/terminfo',      # bash/nano terminal escape tables
    'FFiles/nano',              # nano editor + bundled terminfo copy
    'res/images',               # AOSP classic-UI images, unused by themed UI
]
# languages: keep en + bn_BD + hi_IN (device markets)
LANG_KEEP = {'en.xml', 'bn_BD.xml', 'hi_IN.xml'}
# paytrigger: Mediatek factory pay-trigger test stack (recovery has zero refs)
PAYTRIGGER_FILES = [
    'vendor/bin/paytrigger_test',
    'vendor/bin/vendor.mediatek.hardware.paytrigger@1.0-service',
    'vendor/lib64/vendor.mediatek.hardware.paytrigger@1.0.so',
    'vendor/lib64/hw/paytrigger.trustonic.so',
    'vendor/etc/vintf/manifest/vendor.mediatek.hardware.paytrigger@1.0-service.xml',
]
# toybox provides sed/tar; the gnu twins are never referenced by name
GNU_TOOLS = ['sbin/gnused', 'sbin/gnutar']

# Tier 2 - OrangeFox niceties (explicitly approved: "no generic stuff"):
# NOTE (twrp-12.1 branch, 2026-11-14): 'system/bin/fastbootd' was REMOVED
# from this cut list - fastbootd is a hard requirement here (adb reboot
# fastbootd must work from this ramdisk; it is the only route to flash
# super/logical partitions while the recovery occupies boot_a). Re-adding
# it would silently break that; the CI backstop also runs --no-cut.
TIER2_FILES = [
    'system/bin/update_engine_sideload',   # A/B payload sideload path
    'system/bin/zip', 'sbin/zip',          # zip CLI (installer uses libziparchive)
    'system/bin/avbctl',
]
# NOTE: sbin/magiskboot is KEPT - OF_avb10.zip + OF_verity_crypt.zip and
# foxstart.sh reference /sbin/magiskboot (AVB patch / dm-verity tools).
TIER2_TREES = [
    'system/etc/init/fastbootd.rc',        # file, but listed here for clarity
]
# theme fonts: keep InterDisplay (OrangeFox 12.1 default) + Roboto (fallback)
FONT_KEEP = {'InterDisplay-Medium.ttf', 'InterDisplay-Regular.ttf',
             'Roboto-Medium.ttf', 'Roboto-Regular.ttf'}

# fastbootd rc: keep the file but drop the service block? simpler: cut binary only
TIER2_TREES = []

# Extra verified cuts:
#  - hwcomposer.mt6768.so: no composer service binary exists in the ramdisk
#    and no ELF NEEDs it -> never loaded. libxml2.so's only user WAS
#    hwcomposer -> both go.
#  - system/bin/snapuserd + system/bin/e2fsck: dead duplicates - init's
#    switch_root() moves first_stage_ramdisk/* over /, so the first_stage
#    copies replace these files at boot.
# NOTE (twrp-12.1 branch): android.hardware.fastboot@1.1.so (fastbootd's
# HAL) was REMOVED from this list on 2026-11-14 - fastbootd is required on
# this branch, and its HAL must not be orphan-swept. On a plain TWRP image
# the entry is typically absent anyway, making this a no-op either way.
EXTRA_CUTS = [
    'vendor/lib64/hw/hwcomposer.mt6768.so',
    'system/lib64/libxml2.so',
    'system/bin/snapuserd',      # dead dup of first_stage_ramdisk copy
    'system/bin/e2fsck',         # dead dup of first_stage_ramdisk copy
    # --- orphan sweep (verified: no DT_NEEDED, no dlopen refs, no script refs) ---
    'system/bin/linker_asan64',  # ASAN runtime linker - no ASAN binaries present
    'system/lib64/libclang_rt.ubsan_standalone-aarch64-android.so',
    'system/lib64/libncurses.so',   # only user was nano (cut)
    'system/lib64/libtwrpmtp-ffs.so',   # MTP ffs lib - zero references
    'system/bin/xz', 'system/bin/lzma', # CLIs (liblzma stays: libunwindstack)
    'system/bin/bzip2', 'system/bin/bc',
    'system/lib64/libntfs-3g.so', 'system/bin/mount.ntfs',
    'system/bin/mkfs.ntfs', 'system/bin/fsck.ntfs',
    'system/lib64/libnl.so',
    'system/lib64/android.hardware.health.storage@1.0.so',
    'system/lib64/android.hardware.health.storage-V1-ndk_platform.so',
    'system/bin/modprobe',
    'system/lib64/android.hardware.vibrator@1.0.so',
    'system/lib64/android.hardware.vibrator@1.1.so',
    'system/lib64/android.hardware.vibrator@1.2.so',
    'system/lib64/android.hardware.vibrator-V1-cpp.so',
    'system/lib64/android.hardware.vibrator-V2-cpp.so',
    'system/lib64/android.hardware.vibrator-V1-ndk_platform.so',
    'system/lib64/android.hardware.vibrator-V2-ndk.so',
    'system/lib64/android.hardware.vibrator-V2-ndk_platform.so',
    'system/lib64/libdmabufheap.so',
    'system/bin/lptools',
    'system/lib64/libservices.so', 'system/lib64/libcppbor.so',
    'system/lib64/libtinyalsa.so',
    'FFiles/ps',                    # toybox ps covers it
    'system/bin/flash_image', 'system/bin/dump_image', 'system/bin/erase_image',
    'system/lib64/libflashutils.so', 'system/lib64/libbmlutils.so',
    'system/lib64/libmmcutils.so',
    'system/lib64/libnos_transport.so', 'system/lib64/libnos_datagram.so',
    'system/lib64/libhardware_legacy.so',
    'system/lib64/android.hidl.token@1.0-utils.so',
    'system/bin/twrp', 'system/bin/ozip_decrypt', 'system/bin/openaes',
    'system/bin/bu',
    'system/lib64/libnetd_client.so',   # libc dlopens it lazily, falls back
    'system/bin/zipinfo', 'system/bin/ziptool',
]
# deliberately KEPT despite no static refs (runtime/dlopen/rc users):
#   sbin/magiskboot (OF_avb10/OF_verity_crypt/foxstart), sbin/bash (/sbin/sh),
#   system/bin/minadbd (sideload), pigz/unpigz (backup), system/bin/charger,
#   watchdogd, bootctl, resetprop, simg2img, unzip, getevent (touch debug),
#   android.hardware.{boot,health}@*-service (rc), vold_prepare_subdirs,
#   fscryptpolicyget + libincfs.so (FBE), liblzma.so (libunwindstack),
#   exfat/fat tools (external SD), vendor/thh/ta (TEE), mkfs.fat/fatlabel.

# ICU stub: when enabled, replace libandroidicu.so with a no-ICU stub and drop
# libicuuc.so + libicui18n.so (libsqlite collation only - keystore2 uses none)
ICU_STUB_REPLACE = 'system/lib64/libandroidicu.so'
ICU_STUB_DROP = ['system/lib64/libicuuc.so', 'system/lib64/libicui18n.so']


def build_cut_set(stub_icu=False, tier2=True):
    cut = set()

    def add_file(p):
        cut.add(p)

    def add_tree(p):
        cut.add(p)
        cut.add(p + '/')

    for f in TIER1_FILES + GNU_TOOLS + PAYTRIGGER_FILES + EXTRA_CUTS:
        add_file(f)
    for t in TIER1_TREES:
        add_tree(t)
    if tier2:
        for f in TIER2_FILES:
            add_file(f)
    return cut


def is_cut(name, cut_set):
    """name = cpio entry name (no leading ./). Trees match by prefix."""
    if name in cut_set:
        return True
    for t in TIER1_TREES + TIER2_TREES:
        if name.startswith(t + '/'):
            return True
    # languages
    if name.startswith('twres/languages/') and name.endswith('.xml'):
        return os.path.basename(name) not in LANG_KEEP
    # fonts (tier2: also drop unused theme fonts)
    if name.startswith('twres/fonts/') and name.endswith('.ttf'):
        if os.path.basename(name) not in FONT_KEEP and \
           os.path.basename(name) != 'wqy-microhei.ttf':   # wqy always cut
            return True
    return False


# ----------------------------------------------------------------------------
# cpio newc parsing
# ----------------------------------------------------------------------------
class Entry:
    __slots__ = ('raw', 'name', 'mode', 'fsize', 'is_dir', 'is_symlink',
                 'data', 'namesize', 'hdrlen')


def parse_cpio(raw):
    entries = []
    pos = 0
    n = len(raw)
    while pos < n:
        if raw[pos:pos + 6] != b'070701':
            nxt = raw.find(b'070701', pos)
            if nxt == -1:
                break
            pos = nxt
        hdr = raw[pos:pos + 110]
        fields = [int(hdr[6 + i * 8:6 + (i + 1) * 8], 16) for i in range(13)]
        (ino, mode, uid, gid, nlink, mtime, fsize, dmaj, dmin,
         rmaj, rmin, namesize, chksum) = fields
        name = raw[pos + 110:pos + 110 + namesize - 1].decode('utf-8', 'replace')
        hdrlen = (110 + namesize + 3) & ~3
        fstart = pos + hdrlen
        fend = fstart + fsize
        if name == 'TRAILER!!!':
            entries.append(None)   # marker
            break
        e = Entry()
        e.raw = raw[pos:fend]
        e.name = name
        e.mode = mode
        e.fsize = fsize
        e.is_dir = (mode & 0o170000) == 0o040000
        e.is_symlink = (mode & 0o170000) == 0o120000
        e.data = raw[fstart:fend]
        e.hdrlen = hdrlen
        entries.append(e)
        pos = (fend + 3) & ~3
    return entries


def rebuild_cpio(entries):
    """entries: list of Entry. Raw-slice entries keep original bytes;
    constructed entries (raw=None) are serialized from fields."""
    out = bytearray()
    for e in entries:
        if e is None:
            continue
        if e.raw is not None:
            out += e.raw
            out += b'\0' * ((-e.fsize) % 4)
        else:
            nb = e.name.encode() + b'\0'
            hdr = bytearray(110)
            hdr[0:6] = b'070701'
            vals = [0, e.mode, 0, 0, 1, 0, e.fsize, 0, 0, 0, 0, len(nb), 0]
            for i, v in enumerate(vals):
                hdr[6 + i * 8:6 + (i + 1) * 8] = b'%08X' % v
            out += hdr + nb
            out += b'\0' * ((-(110 + len(nb))) % 4)
            out += e.data
            out += b'\0' * ((-e.fsize) % 4)
    # proper newc trailer. 13 header fields x 8 chars: namesize is field 11
    # (header bytes [94:102]), check is field 12 ([102:110]).
    tn = b'TRAILER!!!\0'
    out += b'070701' + b'0' * 88 + b'%08X' % len(tn) + b'0' * 8 + tn
    out += b'\0' * ((-len(out)) % 4)
    out += b'\0' * ((-len(out)) % 512)   # pad like mkbootfs (512)
    return bytes(out)


# ----------------------------------------------------------------------------
# metadata regeneration
# ----------------------------------------------------------------------------
def gen_metadata(entries):
    """Regenerate OrangeFox's two ramdisk integrity manifests, matching the
    original formats exactly (verified against a shipped image):
      ramdisk-files.txt:        '.' then every entry name (dirs, symlinks,
                                hardlink dups, and both metadata files)
      ramdisk-files.sha256sum:  '<sha256>  ./<path>' for every non-dir,
                                non-symlink entry (hardlink dups hash as
                                empty, like the original), INCLUDING the
                                new ramdisk-files.txt, EXCLUDING itself.
    Because the sha file must hash the NEW txt content, this is a two-phase
    function: it mutates/creates the txt entry first, then builds the sha.
    """
    names = ['.'] + sorted(e.name for e in entries if e is not None)
    txt = ('\n'.join(names) + '\n').encode()
    replace_entry(entries, 'ramdisk-files.txt', txt, 0o100644)
    lines = []
    for e in entries:
        if e is None or e.is_dir or e.is_symlink:
            continue
        if e.name == 'ramdisk-files.sha256sum':
            continue
        h = hashlib.sha256(e.data).hexdigest()
        lines.append(f'{h}  ./{e.name}')
    sha = ('\n'.join(sorted(lines)) + '\n').encode() if lines else b''
    replace_entry(entries, 'ramdisk-files.sha256sum', sha, 0o100644)


def replace_entry(entries, name, blob, mode=0o100644):
    for i, e in enumerate(entries):
        if e is not None and e.name == name:
            ne = Entry()
            ne.raw = None
            ne.name = name
            ne.mode = mode
            ne.fsize = len(blob)
            ne.is_dir = False
            ne.is_symlink = False
            ne.data = blob
            ne.hdrlen = 0
            entries[i] = ne
            return True
    ne = Entry()
    ne.raw = None
    ne.name = name
    ne.mode = mode
    ne.fsize = len(blob)
    ne.is_dir = False
    ne.is_symlink = False
    ne.data = blob
    ne.hdrlen = 0
    entries.append(ne)
    return False


# ----------------------------------------------------------------------------
# boot image
# ----------------------------------------------------------------------------
def parse_bootimg(data):
    assert data[:8] == b'ANDROID!'
    h = {}
    h['kernel_size'], h['kernel_addr'] = struct.unpack('<II', data[8:16])
    h['ramdisk_size'], h['ramdisk_addr'] = struct.unpack('<II', data[16:24])
    h['second_size'], h['second_addr'] = struct.unpack('<II', data[24:32])
    h['tags_addr'], = struct.unpack('<I', data[32:36])
    h['page_size'], h['header_version'] = struct.unpack('<II', data[36:44])
    h['os_version'], = struct.unpack('<I', data[44:48])
    h['name'] = data[48:64].split(b'\0')[0]
    h['cmdline'] = data[64:576].split(b'\0')[0]
    h['id'] = data[576:608]
    h['extra_cmdline'] = data[608:1632].split(b'\0')[0]
    # v1/v2 tail
    h['recovery_dtbo_size'], = struct.unpack('<I', data[1632:1636])
    h['recovery_dtbo_offset'], = struct.unpack('<Q', data[1636:1644])
    h['header_size'], = struct.unpack('<I', data[1644:1648])
    if h['header_version'] == 2:
        h['dtb_size'], h['dtb_addr'] = struct.unpack('<II', data[1648:1656])
    else:
        h['dtb_size'] = h['dtb_addr'] = 0
    p = h['page_size']
    off = p
    h['kernel'] = data[off:off + h['kernel_size']]
    off += ((h['kernel_size'] + p - 1) // p) * p
    h['ramdisk'] = data[off:off + h['ramdisk_size']]
    off += ((h['ramdisk_size'] + p - 1) // p) * p
    off += ((h['second_size'] + p - 1) // p) * p
    h['second'] = data[off:off + h['second_size']] if h['second_size'] else b''
    off += ((h['second_size'] + p - 1) // p) * p
    h['dtb'] = data[off:off + h['dtb_size']] if h['dtb_size'] else b''
    return h


def build_bootimg(h, ramdisk_blob):
    p = h['page_size']
    # header: clone original bytes, patch sizes + id
    hdr = bytearray(h['orig_header'])

    def put(off, fmt, val):
        struct.pack_into(fmt, hdr, off, val)
    put(16, '<I', len(ramdisk_blob))
    # recompute id (mkbootimg v2 algo): sha1 over sizes+blobs
    sha = hashlib.sha1()
    for blob in (h['kernel'], ramdisk_blob, h['second'], h['dtb']):
        if blob is not None:
            sha.update(struct.pack('<I', len(blob)))
            sha.update(blob)
    put(576, '<20s', sha.digest())

    out = bytearray()
    out += hdr
    out += b'\0' * ((-len(hdr)) % p)
    for blob in (h['kernel'], ramdisk_blob, h['second'], h['dtb']):
        if not blob:
            continue
        out += blob
        out += b'\0' * ((-len(blob)) % p)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('img')
    ap.add_argument('out')
    ap.add_argument('--report-only', action='store_true')
    ap.add_argument('--no-tier2', action='store_true',
                    help='keep update_engine_sideload/zip CLIs/theme fonts')
    ap.add_argument('--no-cut', action='store_true',
                    help='NO-CUT mode: keep every ramdisk entry byte-identical; '
                         'only recompress (gzip-9/zopfli) and repack the image. '
                         'Used as the size backstop on the twrp-12.1 branch so '
                         'fastbootd can never be cut.')
    ap.add_argument('--icu-stub', metavar='STUB_SO',
                    help='replace libandroidicu.so with the stub and drop ICU')
    ap.add_argument('--zopfli', metavar='BIN',
                    help='use this zopfli binary for ramdisk compression')
    ap.add_argument('--zopfli-iterations', type=int, default=10)
    ap.add_argument('--save-cpio', metavar='PATH', help='dump the pruned cpio to PATH')
    args = ap.parse_args()

    data = open(args.img, 'rb').read()
    h = parse_bootimg(data)
    h['orig_header'] = data[:1660] if h['header_version'] == 2 else data[:1648]
    print(f'image      : {len(data):,} bytes')
    print(f'kernel     : {h["kernel_size"]:,} ({h["kernel_size"]/1048576:.2f} MiB)')
    print(f'ramdisk gz : {h["ramdisk_size"]:,} ({h["ramdisk_size"]/1048576:.2f} MiB)')
    print(f'dtb        : {h["dtb_size"]:,}')
    print(f'header v{h["header_version"]}, page {h["page_size"]}, '
          f'name={h["name"].decode()}')

    cpio = gzip.decompress(h['ramdisk'])
    print(f'ramdisk raw: {len(cpio):,} ({len(cpio)/1048576:.2f} MiB)')

    entries = parse_cpio(cpio)
    trailer = entries and entries[-1] is None
    if trailer:
        entries = entries[:-1]
    print(f'entries    : {len(entries)}')

    cut_set = build_cut_set(tier2=not args.no_tier2) if not args.no_cut else set()
    if args.no_cut:
        kept, removed = list(entries), []
        print('mode       : NO-CUT (all entries preserved, compression only)')
    else:
        kept, removed = [], []
        for e in entries:
            if is_cut(e.name, cut_set):
                removed.append(e)
            else:
                kept.append(e)

    removed_bytes = sum(e.fsize for e in removed if not e.is_dir)
    print(f'cut        : {len(removed)} entries, {removed_bytes/1048576:.2f} MiB payload')
    for e in sorted(removed, key=lambda x: -x.fsize)[:20]:
        if not e.is_dir:
            print(f'   {e.fsize/1024:8.0f} KiB  {e.name}')

    # drop now-empty dirs (terminfo/, res/images/, FFiles/nano trees) -
    # only in cut mode; in --no-cut mode every original dir must survive
    if args.no_cut:
        kept2 = kept
    else:
        dir_names = {e.name for e in kept if e.is_dir}
        child_prefixes = set()
        for e in kept:
            if not e.is_dir:
                parts = e.name.split('/')
                for i in range(1, len(parts)):
                    child_prefixes.add('/'.join(parts[:i]))
        kept2 = [e for e in kept if not (e.is_dir and e.name not in child_prefixes
                                         and e.name != '.')]
        if len(kept2) != len(kept):
            print(f'dropped {len(kept)-len(kept2)} emptied dirs')

    # ICU stub swap FIRST so the metadata manifests reflect the final set
    # (never in --no-cut mode: that mode must not modify any entry)
    if args.icu_stub and not args.no_cut:
        stub = open(args.icu_stub, 'rb').read()
        replace_entry(kept2, ICU_STUB_REPLACE, stub, 0o100644)
        kept2 = [e for e in kept2 if e is None or e.name not in ICU_STUB_DROP]
        print(f'icu stub  : {ICU_STUB_REPLACE} <- {len(stub)} bytes, '
              f'dropped {ICU_STUB_DROP}')

    # regenerate OrangeFox's ramdisk integrity manifests - only when
    # entries were cut. In --no-cut mode nothing changed (and a plain TWRP
    # ramdisk has no ramdisk-files.txt at all; injecting one would modify
    # the image), so the manifests stay exactly as built.
    if not args.no_cut:
        gen_metadata(kept2)

    new_cpio = rebuild_cpio(kept2)
    if args.save_cpio:
        open(args.save_cpio, 'wb').write(new_cpio)
        print(f'cpio saved : {args.save_cpio}')

    # compress: zopfli (best, slow) or gzip -9
    import subprocess, tempfile
    if args.zopfli:
        with tempfile.NamedTemporaryFile(suffix='.cpio', delete=False) as tf:
            tf.write(new_cpio)
            cpio_path = tf.name
        gz_path = cpio_path + '.gz'
        cmd = [args.zopfli, '-c', '-i', str(args.zopfli_iterations), cpio_path]
        with open(gz_path, 'wb') as out:
            r = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE)
        if r.returncode != 0:
            print('zopfli failed, falling back to gzip -9:',
                  r.stderr.decode()[:200])
            new_gz = gzip.compress(new_cpio, 9)
        else:
            new_gz = open(gz_path, 'rb').read()
        os.unlink(cpio_path)
        if os.path.exists(gz_path):
            os.unlink(gz_path)
    else:
        new_gz = gzip.compress(new_cpio, 9)
    print(f'new cpio   : {len(new_cpio):,} ({len(new_cpio)/1048576:.2f} MiB)')
    print(f'new gz     : {len(new_gz):,} ({len(new_gz)/1048576:.2f} MiB)')

    img = build_bootimg(h, new_gz)
    print(f'new image  : {len(img):,} ({len(img)/1048576:.2f} MiB)  '
          f'[limit 33,484,800 = 31.93 MiB usable]')
    fits = len(img) <= 33_484_800
    print('STATUS     :', 'FITS stock 32 MiB boot_a' if fits else
          'OVER 32 MiB (Option C repartition needed)')

    if not args.report_only:
        open(args.out, 'wb').write(img)
        print(f'written    : {args.out}')
        # sanity: re-parse
        h2 = parse_bootimg(img)
        cpio2 = gzip.decompress(h2['ramdisk'])
        entries2 = parse_cpio(cpio2)
        n_files2 = sum(1 for e in entries2 if e is not None and not e.is_dir)
        print(f'sanity     : reparsed {n_files2} files, '
              f'kernel identical={h2["kernel"] == h["kernel"]}, '
              f'dtb identical={h2["dtb"] == h["dtb"]}')


if __name__ == '__main__':
    main()
