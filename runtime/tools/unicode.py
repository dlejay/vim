#!/usr/bin/env python3
import urllib.request
import unicodedata
import os

# ─── URLs for Unicode data ───────────────────────────────────────────────────
COMBINING_URL = 'https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt'
WORD_BREAK_URL = (
    'https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/'
    'WordBreakProperty.txt'
)

# ─── Utility functions ───────────────────────────────────────────────────────
def download_lines(url):
    """Fetch a URL and return its content as a list of lines."""
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode('utf-8').splitlines()


def make_intervals(cps):
    """Merge sorted codepoints into (start, end) ranges."""
    intervals = []
    if not cps:
        return intervals
    start = prev = cps[0]
    for cp in cps[1:]:
        if cp == prev + 1:
            prev = cp
        else:
            intervals.append((start, prev))
            start = prev = cp
    intervals.append((start, prev))
    return intervals


def format_range_comment(start, end):
    """Describe a range by Unicode name(s); return empty if unavailable."""
    try:
        first = unicodedata.name(chr(start))
    except ValueError:
        return ''
    if start == end:
        return first
    try:
        last = unicodedata.name(chr(end))
    except ValueError:
        return ''
    return f"{first}..{last}"


# ─── Combining-class table ──────────────────────────────────────────────────

def parse_combining(lines):
    """Extract codepoints whose combining class != 0."""
    return sorted(
        int(fields[0], 16)
        for ln in lines if ln and not ln.startswith('#')
        for fields in [ln.split(';')]
        if fields[3] != '0'
    )


def generate_combining_inc(intervals, outname='unicode_is_combining.inc'):
    """Write .inc file of {start,end} pairs with comments."""
    entries = []
    for a, b in intervals:
        entry = f"    {{0x{a:X}, 0x{b:X}}},"
        comment = format_range_comment(a, b)
        entries.append((entry, comment))

    width = max(len(e) for e, _ in entries)
    lines = ['// Auto-generated combining-mark ranges; do not edit']
    for e, c in entries:
        pad = ' ' * (width - len(e) + 1) if c else ''
        suffix = f"// {c}" if c else ''
        lines.append(f"{e}{pad}{suffix}")

    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote combining table to {outname}")


# ─── Word-break property table ───────────────────────────────────────────────

def parse_wordbreak(lines):
    """Extract (start,end,property) triples from WordBreakProperty.txt."""
    intervals = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        span, prop = ln.split('#', 1)[0].split(';')[:2]
        start_str, end_str = (span.split('..') + [span])[:2]
        start, end = int(start_str, 16), int(end_str, 16)
        intervals.append((start, end, f"U_WB_{prop.strip()}"))
    return intervals


def merge_intervals(intervals):
    """Merge contiguous intervals having identical property."""
    merged = []
    for start, end, prop in sorted(intervals, key=lambda x: x[0]):
        if merged and merged[-1][2] == prop and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end), prop)
        else:
            merged.append((start, end, prop))
    return merged


def fill_gaps(intervals, max_code=0x10FFFF):
    """Insert 'Other' spans where no property was defined."""
    filled, prev_end = [], -1
    for start, end, prop in intervals:
        if start > prev_end + 1:
            filled.append((prev_end + 1, start - 1, 'U_WB_Other'))
        filled.append((start, end, prop))
        prev_end = end
    if prev_end < max_code:
        filled.append((prev_end + 1, max_code, 'U_WB_Other'))
    return filled


def generate_wordbreak_inc(intervals, outname='unicode_word_break.inc'):
    """Write .inc file of {start,end,prop} entries with comments."""
    entries = []
    for a, b, p in intervals:
        entry = f"    {{0x{a:X}, 0x{b:X}, {p}}},"
        comment = '' if p.endswith('Other') else format_range_comment(a, b)
        entries.append((entry, comment))

    width = max(len(e) for e, _ in entries)
    lines = ['// Auto-generated from WordBreakProperty.txt; do not edit']
    for e, c in entries:
        pad = ' ' * (width - len(e) + 1) if c else ''
        suffix = f"// {c}" if c else ''
        lines.append(f"{e}{pad}{suffix}")

    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote word-break table to {outname}")


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    # Combining-class
    ucd = download_lines(COMBINING_URL)
    cps = parse_combining(ucd)
    generate_combining_inc(make_intervals(cps))

    # Word-break
    wb = download_lines(WORD_BREAK_URL)
    wb_int = parse_wordbreak(wb)
    merged = merge_intervals(wb_int)
    filled = fill_gaps(merged)
    generate_wordbreak_inc(merged := merge_intervals(filled))


if __name__ == '__main__':
    main()
