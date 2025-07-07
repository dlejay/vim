/*
 * 
 *  unicode.c – functions related to the Unicode® Standard
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

// WordBreakProperty_Property_T is typedef'ed in unicode.h

struct wb_interval
{
    unsigned int    first;
    unsigned int    last;
    Word_Break_T    wb;
};

/*
 *  Table 3. WordBreakProperty Property Values
 *
 *  Ordered list of intervals, for binary search.
 *
 *  Obtained from WordBreakProperty-16.0.0.txt
 *  thanks to ../runtime/tools/unicode.py
 *
 *  The table is too big and stays in its own file.
 */
static const struct wb_interval WordBreakProperty[] =
{
#include "WordBreakProperty.inc"
};

/*
 *  Returns the WordBreakProperty property of a Unicode character.
 */
Word_Break_T
unicode_get_word_break_value(int c)
{
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
	if (WordBreakProperty[mid].last < (unsigned int)c)
	    bot = mid + 1;
	else if (WordBreakProperty[mid].first > (unsigned int)c)
	    top = mid - 1;
	else
	    return WordBreakProperty[mid].wb;
    }
    return WB_Other;
}
