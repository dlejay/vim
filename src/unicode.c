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

#include "vim.h"

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

// codepoint_T and Word_Break_T are typedef'ed in unicode.h

struct wb_interval
{
    codepoint_T first;
    codepoint_T last;
    u_word_break_T wb;
};

/*
 *  Returns the WordBreakProperty property of a Unicode character
 *  by performing a binary search in an ordered list of invervals
 *  which is built from:
 *
 *  WordBreakProperty-16.0.0.txt
 *
 *  thanks to ../runtime/tools/unicode.py
 *
 *  The table is too big and stays in its own file.
 */
u_word_break_T
unicode_get_word_break_property(codepoint_T c)
{
    struct wb_interval WordBreakProperty[] = {
#include "WordBreakProperty.inc"
    };
    int bot = 0;
    int top = ARRAY_LENGTH(WordBreakProperty) - 1;
    int mid = (bot + top) / 2;

    // Shortcut for Latin1 characters.
    if (c < 0x100)
        top = 42;

    // binary search in table
    while (top >= bot)
    {
        mid = (bot + top) / 2;
        if (WordBreakProperty[mid].last < c)
            bot = mid + 1;
        else if (WordBreakProperty[mid].first > c)
            top = mid - 1;
        else
            return WordBreakProperty[mid].wb;
    }
    return U_WB_Other;
}
