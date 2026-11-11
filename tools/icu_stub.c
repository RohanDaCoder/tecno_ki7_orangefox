/*
 * icu_stub.c -- freestanding libandroidicu replacement for recovery builds.
 *
 * libsqlite links libandroidicu (21 symbols) for ICU collation. In the
 * recovery ramdisk the ONLY consumer chain is keystore2 -> libsqlite, and
 * keystore2 uses plain BINARY collation - the ICU path exists only so that
 * sqlite3_open() can register the "icu" collators at init.
 *
 * This stub makes that init SUCCEED with degenerate-but-safe semantics:
 *   - ucol_open returns a dummy non-NULL handle with *status = U_ZERO_ERROR
 *     (returning NULL/error would make sqlite3IcuInit() fail and could make
 *     sqlite3_open() fail -> keystore2 dead -> FBE decryption dead)
 *   - ucol_strcoll* returns 0 ("equal") - only affects COLLATE ICU queries,
 *     which keystore2 never issues
 *   - u_strToUpper/u_strToLower return identity copies (LIKE stays
 *     case-sensitive - acceptable in recovery)
 *   - ubrk_open/uregex_open return NULL with U_UNSUPPORTED_ERROR; callers
 *     check the status flag and degrade gracefully (FTS/regex unused)
 *
 * No libc calls at all: own copy loop only. Build freestanding:
 *   clang -target aarch64-linux-android30 -shared -fPIC -O2 -nostdlib \
 *         -Wl,-soname,libandroidicu.so -o libandroidicu.so icu_stub.c
 */
typedef int int32_t4;
#define NULL ((void*)0)

typedef unsigned short UChar;   /* UTF-16 code unit */
typedef void* UCollator;
typedef void* UBreakIterator;
typedef void* URegularExpression;
typedef void* UCharIterator;

/* keep the original typedefs simple; signatures only need ABI compatibility */
typedef int UErrorCode;         /* int32 */

#define U_ZERO_ERROR              0
#define U_BUFFER_OVERFLOW_ERROR  15
#define U_UNSUPPORTED_ERROR      16
#define U_STRING_NOT_TERMINATED_WARNING  -124

static int32_t4 cplen(const UChar* s, int32_t4 n) {
    /* n<0 means NUL-terminated */
    if (n >= 0) return n;
    int32_t4 i = 0;
    while (s[i]) i++;
    return i;
}

static void ccopy(UChar* d, const UChar* s, int32_t4 n) {
    for (int32_t4 i = 0; i < n; i++) d[i] = s[i];
}

__attribute__((visibility("default")))
const char* u_errorName_android(int code) {
    (void)code;
    return "U_ZERO_ERROR";
}

__attribute__((visibility("default")))
unsigned int u_foldCase_android(unsigned int c, unsigned int options) {
    (void)options;
    return c;   /* identity */
}

__attribute__((visibility("default")))
int u_isspace_android(unsigned int c) {
    return c == 0x20 || (c >= 0x09 && c <= 0x0d) || c == 0x85 || c == 0xa0;
}

__attribute__((visibility("default")))
int32_t4 u_strToUpper_android(UChar* dest, int32_t4 destCapacity,
                              const UChar* src, int32_t4 srcLength,
                              const char* locale, UErrorCode* err) {
    (void)locale;
    int32_t4 n = cplen(src, srcLength);
    if (n > destCapacity) {
        if (err) *err = U_BUFFER_OVERFLOW_ERROR;
        return n;
    }
    ccopy(dest, src, n);
    if (err) *err = U_ZERO_ERROR;
    return n;
}

__attribute__((visibility("default")))
int32_t4 u_strToLower_android(UChar* dest, int32_t4 destCapacity,
                              const UChar* src, int32_t4 srcLength,
                              const char* locale, UErrorCode* err) {
    return u_strToUpper_android(dest, destCapacity, src, srcLength, locale, err);
}

__attribute__((visibility("default")))
int32_t4 u_strToUTF8_android(char* dest, int32_t4 destCapacity,
                             int32_t4* destLength,
                             const UChar* src, int32_t4 srcLength,
                             UErrorCode* status) {
    /* approximate: strip to 8-bit (surrogates collapsed to '?') */
    int32_t4 n = cplen(src, srcLength);
    if (destLength) *destLength = 0;
    if (n > destCapacity) {
        if (status) *status = U_BUFFER_OVERFLOW_ERROR;
        return n;
    }
    for (int32_t4 i = 0; i < n; i++) {
        UChar u = src[i];
        dest[i] = (u < 0x80) ? (char)u : '?';
    }
    if (destLength) *destLength = n;
    if (status) *status = U_ZERO_ERROR;
    return n;
}

__attribute__((visibility("default")))
UBreakIterator* ubrk_open_android(const char* type, const char* locale,
                                  const UChar* text, int32_t4 textLength,
                                  UErrorCode* status) {
    (void)type; (void)locale; (void)text; (void)textLength;
    if (status) *status = U_UNSUPPORTED_ERROR;
    return (UBreakIterator*)NULL;
}

__attribute__((visibility("default")))
void ubrk_close_android(UBreakIterator* bi) { (void)bi; }

__attribute__((visibility("default")))
int32_t4 ubrk_first_android(UBreakIterator* bi) { (void)bi; return 0; }

__attribute__((visibility("default")))
int32_t4 ubrk_next_android(UBreakIterator* bi) { (void)bi; return -1; }

__attribute__((visibility("default")))
int32_t4 ubrk_current_android(UBreakIterator* bi) { (void)bi; return -1; }

__attribute__((visibility("default")))
UCollator* ucol_open_android(const char* locale, UErrorCode* status) {
    (void)locale;
    if (status) *status = U_ZERO_ERROR;
    return (UCollator*)1;   /* dummy non-NULL handle */
}

__attribute__((visibility("default")))
void ucol_close_android(UCollator* coll) { (void)coll; }

__attribute__((visibility("default")))
void ucol_setAttribute_android(UCollator* coll, int attr, int value,
                               UErrorCode* status) {
    (void)coll; (void)attr; (void)value;
    if (status) *status = U_ZERO_ERROR;
}

__attribute__((visibility("default")))
int ucol_strcoll_android(const UCollator* coll, const UChar* source,
                         int32_t4 sourceLength, const UChar* target,
                         int32_t4 targetLength) {
    (void)coll; (void)source; (void)sourceLength; (void)target; (void)targetLength;
    return 0;   /* treat as equal */
}

__attribute__((visibility("default")))
int ucol_strcollIter_android(const UCollator* coll, UCharIterator* sIter,
                             UCharIterator* tIter, UErrorCode* status) {
    (void)coll; (void)sIter; (void)tIter;
    if (status) *status = U_ZERO_ERROR;
    return 0;
}

__attribute__((visibility("default")))
void uiter_setUTF8_android(UCharIterator* iter, const char* s, int32_t4 length) {
    /* No-op: nothing in the stub path dereferences the iterator. */
    (void)iter; (void)s; (void)length;
}

__attribute__((visibility("default")))
URegularExpression* uregex_open_android(const UChar* pattern,
                                        int32_t4 patternLength,
                                        unsigned int flags,
                                        UErrorCode* status) {
    (void)pattern; (void)patternLength; (void)flags;
    if (status) *status = U_UNSUPPORTED_ERROR;
    return (URegularExpression*)NULL;
}

__attribute__((visibility("default")))
void uregex_close_android(URegularExpression* regexp) { (void)regexp; }

__attribute__((visibility("default")))
int uregex_matches_android(URegularExpression* regexp, int32_t4 startIndex,
                           UErrorCode* status) {
    (void)regexp; (void)startIndex;
    if (status) *status = U_UNSUPPORTED_ERROR;
    return 0;
}

__attribute__((visibility("default")))
void uregex_setText_android(URegularExpression* regexp, const UChar* text,
                            int32_t4 textLength, UErrorCode* status) {
    (void)regexp; (void)text; (void)textLength;
    if (status) *status = U_UNSUPPORTED_ERROR;
}
