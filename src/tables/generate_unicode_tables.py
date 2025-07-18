#!/usr/bin/env python3
import urllib.request, unicodedata

# ─── URLs ────────────────────────────────────────────────────────────────────
UNICODEDATA_URL = 'https://unicode.org/Public/UCD/latest/ucd/UnicodeData.txt'
WORD_BREAK_URL  = 'https://unicode.org/Public/UCD/latest/ucd/auxiliary/WordBreakProperty.txt'
EAW_URL         = 'https://unicode.org/Public/UCD/latest/ucd/EastAsianWidth.txt'
CASEFOLD_URL    = 'https://unicode.org/Public/UCD/latest/ucd/CaseFolding.txt'

# ─── Utils ───────────────────────────────────────────────────────────────────
def download_lines(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode('utf-8').splitlines()

def make_intervals(cps):
    if not cps: return []
    out, a = [], cps[0]
    for i, cp in enumerate(cps[1:], 1):
        if cp != cps[i-1] + 1:
            out.append((a, cps[i-1])); a = cp
    out.append((a, cps[-1])); return out

def format_range_comment(a, b):
    try:     n1 = unicodedata.name(chr(a))
    except ValueError: return ''
    if a == b: return n1
    try:     n2 = unicodedata.name(chr(b))
    except ValueError: return ''
    return f'{n1}..{n2}'

def merge_intervals(runs):
    merged = []
    for a, b, p in sorted(runs, key=lambda r: r[0]):
        if merged and merged[-1][2] == p and a <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b), p)
        else:
            merged.append((a, b, p))
    return merged

# ─── Combining marks (unchanged) ─────────────────────────────────────────────
def parse_combining(ucd):
    return sorted(int(f[0], 16)
                  for l in ucd if l and not l.startswith('#')
                  for f in [l.split(';')] if f[2].startswith('M'))

def gen_combining_inc(r):
    w = max(len(f"    {{0x{a:X}, 0x{b:X}}},") for a, b in r)
    lines = ['/* Auto-generated combining-mark ranges */']
    for a, b in r:
        entry = f"    {{0x{a:X}, 0x{b:X}}},"
        cmt   = format_range_comment(a, b)
        pad   = ' '*(w-len(entry)+1) if cmt else ''
        lines.append(f"{entry}{pad}{'/* '+cmt+' */' if cmt else ''}")
    open('unicode_combining.inc','w',encoding='utf-8').write('\n'.join(lines)+'\n')

# ─── Word-Break ──────────────────────────────────────────────────────────────
def parse_wordbreak(txt):
    runs=[]
    for l in txt:
        l=l.strip()
        if not l or l.startswith('#'): continue
        span, prop = l.split('#',1)[0].split(';')[:2]
        a,b=[int(x,16) for x in (span.split('..')+[span])[:2]]
        runs.append((a,b,f'U_WB_{prop.strip()}'))
    return runs

def fill_wb_gaps(runs, hi=0x10FFFF):
    out, prev = [], -1
    for a,b,p in runs:
        if a>prev+1: out.append((prev+1,a-1,'U_WB_Other'))
        out.append((a,b,p)); prev=b
    if prev<hi: out.append((prev+1,hi,'U_WB_Other'))
    return out

def gen_wb_inc(runs):
    w=max(len(f"    {{0x{a:X}, 0x{b:X}, {p}}},") for a,b,p in runs)
    out=['/* Auto-generated WordBreakProperty */']
    for a,b,p in runs:
        ent=f"    {{0x{a:X}, 0x{b:X}, {p}}},"
        c='' if p.endswith('Other') else format_range_comment(a,b)
        pad=' '*(w-len(ent)+1) if c else ''
        out.append(f"{ent}{pad}{'/* '+c+' */' if c else ''}")
    open('unicode_word_break.inc','w',encoding='utf-8').write('\n'.join(out)+'\n')

# ─── East Asian Width ────────────────────────────────────────────────────────
def parse_eaw(txt):
    runs=[]
    for l in txt:
        l=l.strip()
        if not l or l.startswith('#'): continue
        span,prop=l.split('#',1)[0].split(';')[:2]
        a,b=[int(x,16) for x in (span.split('..')+[span])[:2]]
        runs.append((a,b,f'U_EAW_{prop.strip()}'))
    return runs

def fill_eaw_gaps(runs, hi=0x10FFFF):
    out, prev = [], -1
    for a,b,p in runs:
        if a>prev+1: out.append((prev+1,a-1,'U_EAW_N'))
        out.append((a,b,p)); prev=b
    if prev<hi: out.append((prev+1,hi,'U_EAW_N'))
    return out

def gen_eaw_inc(runs):
    w=max(len(f"    {{0x{a:X}, 0x{b:X}, {p}}},") for a,b,p in runs)
    out=['/* Auto-generated EastAsianWidth */']
    for a,b,p in runs:
        ent=f"    {{0x{a:X}, 0x{b:X}, {p}}},"
        c='' if p.endswith('_N') else format_range_comment(a,b)
        pad=' '*(w-len(ent)+1) if c else ''
        out.append(f"{ent}{pad}{'/* '+c+' */' if c else ''}")
    open('unicode_east_asian_width.inc','w',encoding='utf-8').write('\n'.join(out)+'\n')

# ─── Case-fold + Upper/Lower (inchangés) ─────────────────────────────────────
def parse_casefold(txt):
    pairs=[]
    for l in txt:
        l=l.strip()
        if not l or l.startswith('#'): continue
        f=l.split('#',1)[0].split(';')
        cp=int(f[0],16); st=f[1].strip()
        if st not in ('C','S'): continue
        m=[int(x,16) for x in f[2].split()]
        if len(m)==1: pairs.append((cp,m[0]))
    return sorted(pairs)

def group_pairs(pairs):
    if not pairs: return []
    out=[]; s=pr=pairs[0][0]; d=pairs[0][1]-pairs[0][0]; stride=None
    for cp,mc in pairs[1:]:
        delta=mc-cp; step=cp-pr
        if delta==d and (stride is None or step==stride):
            stride = step if stride is None else stride; pr=cp
        else:
            out.append((s,pr,-1 if s==pr else stride,d))
            s=pr=cp; d=delta; stride=None
    out.append((s,pr,-1 if s==pr else stride,d)); return out

def gen_simple_inc(groups,fname,tag):
    out=[f'/* Auto-generated simple {tag} */']
    for a,b,st,d in groups:
        out.append(f"    {{0x{a:X},0x{b:X},{st},{d}}},")
    open(fname,'w',encoding='utf-8').write('\n'.join(out)+'\n')

def parse_casing(txt):
    up, lo = [], []
    for l in txt:
        l=l.strip()
        if not l or l.startswith('#'): continue
        f=l.split(';'); cp=int(f[0],16)
        if f[12]: up.append((cp,int(f[12],16)))
        if f[13]: lo.append((cp,int(f[13],16)))
    return sorted(up), sorted(lo)

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    # Combining
    ucd = download_lines(UNICODEDATA_URL)
    gen_combining_inc(make_intervals(parse_combining(ucd)))

    # Word-Break
    wb  = merge_intervals(parse_wordbreak(download_lines(WORD_BREAK_URL)))
    wb2 = merge_intervals(fill_wb_gaps(wb))
    gen_wb_inc(wb2)

    # East Asian Width
    ea  = merge_intervals(parse_eaw(download_lines(EAW_URL)))
    ea2 = merge_intervals(fill_eaw_gaps(ea))
    gen_eaw_inc(ea2)

    # Case-fold
    cf = group_pairs(parse_casefold(download_lines(CASEFOLD_URL)))
    gen_simple_inc(cf,'unicode_simple_fold.inc','case-fold')

    # Upper / Lower
    up_pairs, lo_pairs = parse_casing(ucd)
    gen_simple_inc(group_pairs(up_pairs),'unicode_simple_toupper.inc','toupper')
    gen_simple_inc(group_pairs(lo_pairs),'unicode_simple_tolower.inc','tolower')

if __name__ == '__main__':
    main()
