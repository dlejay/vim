/*
 *  unicode.h
 */

#ifndef VIM_UNICODE_H
#define VIM_UNICODE_H

#include <stdint.h>
#include <stdbool.h>

/*
 * ==========================================================================
 *  Unicode data types
 * ==========================================================================
 */

/* -------------------------------------------------------------------------
 * A single Unicode codepoint, as per the Unicode standard:
 *   valid values: 0x0000 .. 0x10FFFF
 *
 *  Vim traditionally passes characters around as plain ‘int’ (see src/mbyte.c
 *  and friends).  That type is signed on all platforms we care about, which
 *  lets functions return –1 or other negative sentinels.  We codify the same
 *  width and behaviour explicitly with int32_t.
 * ------------------------------------------------------------------------- */
typedef int32_t rune_T;


/* -------------------------------------------------------------------------
 *  unicode_is_combining ― true if r has Canonical_Combining_Class ≠ 0
 *
 *  Table source: UnicodeData.txt  → unicode_is_combining.inc
 * ------------------------------------------------------------------------- */
bool
unicode_is_combining(rune_T r);

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

#endif
