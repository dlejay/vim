/*
 *  unicode.h
 */

/*
 * =================================================================
 *
 *		    Unicode® Standard Annex #29
 *
 *	    U N I C O D E  T E X T  S E G M E N T A T I O N
 *
 * =================================================================
 */

#ifndef UNICODE_H
# define UNICODE_H

//  Table 3. Word_Break Property Values
typedef enum {
    WB_Other,
    WB_LF,
    WB_CR,
    WB_ALetter,
    WB_Format,
    WB_Katakana,
    WB_Numeric,
    WB_Extend,
    WB_Newline,
    WB_ExtendNumLet,
    WB_Regional_Indicator,
    WB_Hebrew_Letter,
    WB_Single_Quote,
    WB_Double_Quote,
    WB_MidNum,
    WB_MidLetter,
    WB_MidNumLet,
    WB_WSegSpace,
    WB_ZWJ,
} Word_Break_T;

//  Table 3a. Word_Break Rule Macros
# define AHLetter(p) (p == WB_ALetter || p == WB_Hebrew_Letter)
# define MidNumLetQ(p) (p == WB_MidNumLet || p == WB_Single_Quote)

#endif
