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
 *	§ Unicode® Core Specification
 *	§ Unicode® Standard Annex #29 – UNICODE TEXT SEGMENTATION
 *
 */

#include "unicode.h"
#include <stddef.h>

/*
 * =================================================================
 *
 *		    Unicode® 16.0.0 Core Specification
 *
 * =================================================================
 */

struct interval
{
    rune_T first;
    rune_T last;
};

/*
 * Return true if "r" is in "table[size / sizeof(struct interval)]".
 */
static bool
in_table(struct interval *table, size_t size, rune_T r)
{
    size_t mid = 0, bot = 0, top = 0;

    // first quick check for Latin1 etc. characters
    if (r < table[0].first)
	return false;

    // binary search in table
    bot = 0;
    top = size / sizeof(struct interval) - 1;
    while (top >= bot)
    {
	mid = (bot + top) / 2;
	if (table[mid].last < r)
	    bot = mid + 1;
	else if (table[mid].first > r)
	    top = mid - 1;
	else
	    return true;
    }
    return false;
}

/*
 * -----------------------------------------------------------------
 *  2.1 Combining characters
 * -----------------------------------------------------------------
 */

/*
 * unicode_is_combining – return true if ‘r’ is a Unicode combining mark.
 *
 * A code-point is “combining” if its canonical combining class is not 0.
 * The interval table below is auto-generated from
 *	UnicodeData.txt
 * by
 *	runtime/tools/unicode.py
 * and lives in:
 *	unicode_is_combining.inc
 */
bool
unicode_is_combining(rune_T r)
{
    struct interval combining[] = {
#include "unicode_is_combining.inc"
    };

    return in_table(combining, sizeof(combining), r);
}

/*
 * =================================================================
 *
 *		    Unicode® 16.0.0 Standard Annex #29
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

struct wb_interval
{
    rune_T first;
    rune_T last;
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
unicode_get_word_break_property(rune_T r)
{
    struct wb_interval Word_Break[] = {
#include "unicode_word_break.inc"
    };
    size_t bot = 0, top = 0, mid = 0;

    // LCOV_EXCL_START
    // Defensive check
    if (r < 0 || r > 0x10ffff)
	return U_WB_Other;
    // LCOV_EXCL_STOP

    // binary search in table
    top = sizeof(Word_Break) / sizeof(struct wb_interval) - 1;
    while (top >= bot)
    {
	mid = (bot + top) / 2;
	if (Word_Break[mid].last < r)
	    bot = mid + 1;
	else if (Word_Break[mid].first > r)
	    top = mid - 1;
	else
	    return Word_Break[mid].wb;
    }
    return U_WB_Other;
}

bool
unicode_is_w_seg_space(rune_T c)
{
    return c == 0x0020 ||  // SPACE
	   c == 0x1680 ||  // OGHAM SPACE MARK
	   (c >= 0x2000 && c <= 0x200A) ||  // EN QUAD .. HAIR SPACE
	   c == 0x205F ||  // MEDIUM MATHEMATICAL SPACE
	   c == 0x3000;    // IDEOGRAPHIC SPACE
}
