/*
 *  unicode.h
 */

#ifndef VIM_UNICODE_H
#define VIM_UNICODE_H

#ifdef HAVE_CONFIG_H // GNU autoconf (or something else) was here
# include "auto/config.h"
#endif

/*
 * ==========================================================================
 *  Unicode data types
 * ==========================================================================
 */

/*
 * The Unicode code point range is 0..0x10ffff.
 * Vim assumes sizeof(int) >= 4.
 */
#ifdef HAVE_STDINT_H
# include <stdint.h>
typedef int32_t codepoint_T;
#else
typedef int codepoint_T;
#endif

/*
 * =================================================================
 *
 *		    Unicode® Standard Annex #29
 *
 *	    U N I C O D E  T E X T  S E G M E N T A T I O N
 *
 * =================================================================
 */
//  Table 3. Word_Break Property Values
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

//  Table 3a. Word_Break Rule Macros
#define AHLetter(p) (((p) == U_WB_ALetter) || ((p) == U_WB_Hebrew_Letter))
#define MidNumLetQ(p) (((p) == U_WB_MidNumLet) || ((p) == U_WB_Single_Quote))

#endif
