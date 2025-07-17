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
EAW_URL = 'https://unicode.org/Public/UCD/latest/ucd/EastAsianWidth.txt'
CASEFOLD_URL = 'https://unicode.org/Public/UCD/latest/ucd/CaseFolding.txt'

# ─── Utility functions ───────────────────────────────────────────────────────
def download_lines(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode('utf-8').splitlines()

def make_intervals(cps):
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

# ─── Combining marks table ───────────────────────────────────────────────────
def parse_combining(lines):
    return sorted(
        int(fields[0], 16)
        for ln in lines if ln and not ln.startswith('#')
        for fields in [ln.split(';')]
        if fields[2].startswith('M')
    )

def generate_combining_inc(intervals, outname='unicode_combining.inc'):
    entries = []
    for a, b in intervals:
        entry   = f"    {{0x{a:X}, 0x{b:X}}},"
        comment = format_range_comment(a, b)
        entries.append((entry, comment))
    width = max(len(e) for e, _ in entries)
    lines = ['/* Auto-generated combining-mark ranges from UnicodeData.txt; do not edit */']
    for e, c in entries:
        pad    = ' ' * (width - len(e) + 1) if c else ''
        suffix = f"  /* {c} */" if c else ''
        lines.append(f"{e}{pad}{suffix}")
    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote combining table to {outname}")

# ─── Word-break property table ───────────────────────────────────────────────
def parse_wordbreak(lines):
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
    merged = []
    for start, end, prop in sorted(intervals, key=lambda x: x[0]):
        if merged and merged[-1][2] == prop and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end), prop)
        else:
            merged.append((start, end, prop))
    return merged

def fill_gaps(intervals, max_code=0x10FFFF):
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
    entries = []
    for a, b, p in intervals:
        entry   = f"    {{0x{a:X}, 0x{b:X}, {p}}},"
        comment = '' if p.endswith('Other') else format_range_comment(a, b)
        entries.append((entry, comment))
    width = max(len(e) for e, _ in entries)
    lines = ['/* Auto-generated from WordBreakProperty.txt; do not edit */']
    for e, c in entries:
        pad    = ' ' * (width - len(e) + 1) if c else ''
        suffix = f"  /* {c} */" if c else ''
        lines.append(f"{e}{pad}{suffix}")
    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote word-break table to {outname}")

# ─── East Asian Width “Ambiguous” table ──────────────────────────────────────
def parse_eastasian(lines):
    cps = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        data = ln.split('#', 1)[0]
        span, prop = [p.strip() for p in data.split(';', 1)]
        if prop == 'A':
            start_str, end_str = (span.split('..') + [span])[:2]
            s, e = int(start_str, 16), int(end_str, 16)
            cps.extend(range(s, e+1))
    return sorted(set(cps))

def generate_eastasian_inc(cps, outname='unicode_eastasian_ambiguous.inc'):
    entries = []
    for a, b in make_intervals(cps):
        entry   = f"    {{0x{a:X}, 0x{b:X}}},"
        comment = format_range_comment(a, b)
        entries.append((entry, comment))
    width = max(len(e) for e, _ in entries)
    lines = ['/* Auto-generated EAW=A ranges from EastAsianWidth.txt; do not edit */']
    for e, c in entries:
        pad    = ' ' * (width - len(e) + 1) if c else ''
        suffix = f"  /* {c} */" if c else ''
        lines.append(f"{e}{pad}{suffix}")
    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote EAW=A table to {outname}")

# ─── Simple Case-Folding table ───────────────────────────────────────────────
def parse_casefold(lines):
    pairs = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        fields = ln.split('#',1)[0].split(';')
        cp = int(fields[0], 16)
        status = fields[1].strip()
        if status not in ('C','S'):
            continue
        mapped = [int(x,16) for x in fields[2].split()]
        if len(mapped) != 1:
            continue
        pairs.append((cp, mapped[0]))
    return sorted(pairs)

def group_casefold(pairs):
    groups = []
    if not pairs:
        return groups
    start, prev = pairs[0][0], pairs[0][0]
    diff = pairs[0][1] - pairs[0][0]
    stride = None
    for cp, mc in pairs[1:]:
        d = mc - cp
        s = cp - prev
        if d == diff and (stride is None or s == stride):
            stride = s if stride is None else stride
            prev = cp
        else:
            groups.append((start, prev,
                           -1 if start == prev else stride,
                           diff))
            start = prev = cp
            diff = d
            stride = None
    groups.append((start, prev,
                   -1 if start == prev else stride,
                   diff))
    return groups

def generate_casefold_inc(groups, outname='unicode_simple_fold.inc'):
    lines = ['/* Auto-generated simple case-folding; do not edit */']
    for a,b,step,d in groups:
        lines.append(f"    {{0x{a:X},0x{b:X},{step},{d}}},")
    with open(outname, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote simple case-folding table to {outname}")

# ─── Main entry point ────────────────────────────────────────────────────────
def main():
    # Combining marks
    ucd_lines = download_lines(COMBINING_URL)
    cps       = parse_combining(ucd_lines)
    generate_combining_inc(make_intervals(cps))

    # Word-break properties
    wb_lines     = download_lines(WORD_BREAK_URL)
    wb_intervals = parse_wordbreak(wb_lines)
    merged       = merge_intervals(wb_intervals)
    filled       = fill_gaps(merged)
    final_wb     = merge_intervals(filled)
    generate_wordbreak_inc(final_wb)

    # East Asian Width Ambiguous
    eaw_lines = download_lines(EAW_URL)
    ambiguous = parse_eastasian(eaw_lines)
    generate_eastasian_inc(ambiguous)

    # Simple Case-Folding
    cf_lines = download_lines(CASEFOLD_URL)
    cf_pairs = parse_casefold(cf_lines)
    cf_groups = group_casefold(cf_pairs)
    generate_casefold_inc(cf_groups)

if __name__ == '__main__':
    main()

