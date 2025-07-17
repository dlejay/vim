/*
 *  unicode.h
 */

#ifndef VIM_UNICODE_H
#define VIM_UNICODE_H

#include <stdbool.h>

/*
 * ==========================================================================
 *  Unicode data types
 * ==========================================================================
 */

/* This header defines a portable 'rune_T' type for C89 and later.
 * It selects the smallest signed integer type guaranteed to hold any
 * Unicode code point (up to 0x10FFFF).
 *
 * The selection logic is as follows:
 * 1. If C99 or later is detected, use the precise-width 'int32_t'.
 * 2. Otherwise, check if the standard 'int' is large enough.
 * 3. If not, fall back to 'long int', which C89 guarantees is large enough.
 * 4. If 'long int' is somehow not large enough, raise a compile-time error.
 */

/* The highest valid Unicode code point. */
#define RUNE_MAX 0x10FFFF

/* Include limits.h for INT_MAX and LONG_MAX, which are part of C89. */
#include <limits.h>

/* --- Type Selection --- */

/* Check for C99 or newer, which provides <stdint.h> for int32_t. */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
    #include <stdint.h>
    typedef int32_t rune_T;
    #define RUNE_TYPE_CHOSEN "int32_t"

/* Check if 'int' is at least 32 bits. 0x10FFFF requires 21 bits. */
#elif INT_MAX >= RUNE_MAX
    typedef int rune_T;
    #define RUNE_TYPE_CHOSEN "int"

/* Fallback to 'long int'. C89 guarantees it's at least 32 bits. */
#elif LONG_MAX >= RUNE_MAX
    typedef long int rune_T;
    #define RUNE_TYPE_CHOSEN "long int"

#else
    /* This should not happen on a C89-compliant compiler. */
    #error "Could not find a signed integer type " \
	   "large enough for a Unicode rune."
#endif

/* -------------------------------------------------------------------------
 *  unicode_is_combining ― true if r has Canonical_Combining_Class ≠ 0
 *
 *  Table source: UnicodeData.txt  → unicode_is_combining.inc
 * ------------------------------------------------------------------------- */
bool unicode_is_combining(rune_T r);

/*
 * ==========================================================================
 *
 *   Unicode® Standard Annex #11 - East Asian Width
 *
 * ==========================================================================
 *
 * Reference:
 *  https://www.unicode.org/reports/tr11/
 */
bool unicode_is_eastasian_ambiguous(rune_T r);

/*
 * ==========================================================================
 *
 *   Unicode® Standard Annex #29 - Text Segmentation
 *
 * ==========================================================================
 *
 * These enums model the Unicode Word_Break property, defined in UAX #29
 * Table 3. They serve as inputs to the word boundary algorithm.
 *
 * Reference:
 *   https://unicode.org/reports/tr29/#Word_Boundaries
 */
typedef enum
{
    U_WB_Other,
    U_WB_LF,
    U_WB_CR,
    U_WB_ALetter,
    U_WB_Format,
    U_WB_Katakana,
    U_WB_Numeric,
    U_WB_Extend,
    U_WB_Newline,
    U_WB_ExtendNumLet,
    U_WB_Regional_Indicator,
    U_WB_Hebrew_Letter,
    U_WB_Single_Quote,
    U_WB_Double_Quote,
    U_WB_MidNum,
    U_WB_MidLetter,
    U_WB_MidNumLet,
    U_WB_WSegSpace,
    U_WB_ZWJ,
} u_word_break_T;

/*
 * Rule Macros (UAX #29 Table 3a)
 * These are macro groups used in the word break rules, meant to clarify logic.
 */
#define AHLetter(p) (((p) == U_WB_ALetter) || ((p) == U_WB_Hebrew_Letter))
#define MidNumLetQ(p) (((p) == U_WB_MidNumLet) || ((p) == U_WB_Single_Quote))

/*
 * Return the Word_Break property of a given Unicode codepoint.
 * Falls back to U_WB_Other if the codepoint is outside the defined ranges.
 */
u_word_break_T unicode_get_word_break_property(rune_T r);

/*
 * Test whether a codepoint has the Word_Break=WSegSpace property.
 */
bool unicode_is_w_seg_space(rune_T r);

#endif /* VIM_UNICODE_H */
