/*
 *
 *  unicode.c – functions related to the Unicode® Standard
 *
 *
 *  created by: Damien Lejay
 *
 *
 *  Sections you will find in this file:
 *
 *	§ Unicode® Standard Annex #29 – UNICODE TEXT SEGMENTATION
 *
 */

#include "unicode.h"
#define ARRAY_LENGTH(arr) (sizeof(arr) / sizeof((arr)[0]))
/*
 * =================================================================
 *
 *		    Unicode® Standard Annex #29
 *
 *	    U N I C O D E  T E X T  S E G M E N T A T I O N
 *
 * =================================================================
 */

/*
 * =================================================================
 *
 *  4 Word Boundaries
 *
 * =================================================================
 */

// codepoint_T and u_word_break_T are typedef'ed in unicode.h

struct wb_interval
{
    codepoint_T first;
    codepoint_T last;
    u_word_break_T wb;
};

/*
 *  Returns the Word_Break property of a Unicode character
 *  by performing a binary search in an ordered list of invervals
 *  which is built from:
 *
 *  Word_Break-16.0.0.txt
 *
 *  thanks to ../runtime/tools/unicode.py
 *
 *  The table is too big and stays in its own file.
 */
u_word_break_T
unicode_get_word_break_property(codepoint_T c)
{
    struct wb_interval Word_Break[] = {
#include "unicode_word_break.inc"
    };
    int bot = 0;
    int top = ARRAY_LENGTH(Word_Break) - 1;
    int mid = (bot + top) / 2;

    // LCOV_EXCL_START
    // Defensive check
    if (c < 0 || c > 0x10ffff)
        return U_WB_Other;
    // LCOV_EXCL_STOP

    // binary search in table
    while (top >= bot)
    {
        mid = (bot + top) / 2;
        if (Word_Break[mid].last < c)
            bot = mid + 1;
        else if (Word_Break[mid].first > c)
            top = mid - 1;
        else
            return Word_Break[mid].wb;
    }
    return U_WB_Other;
}

int
unicode_is_w_seg_space(codepoint_T c)
{
    return c == 0x0020 ||  // SPACE
           c == 0x1680 ||  // OGHAM SPACE MARK
           (c >= 0x2000 && c <= 0x200A) ||  // EN QUAD .. HAIR SPACE
           c == 0x205F ||  // MEDIUM MATHEMATICAL SPACE
           c == 0x3000;    // IDEOGRAPHIC SPACE
}
