#!/usr/bin/env python3
r"""Write a copy of tex/ in which every safe occurrence of a glossary term is
marked \termx, for the densely linked editions.

    python3 tools/python/link_all.py [outdir]    (default build/linked-src)

The three ordinary editions are built from tex/ and are untouched; only the
generated tree carries the extra markup, so the sources stay readable and no
occurrence has to be maintained by hand.  Never write \termx yourself.

Which terms are eligible is decided by tools/link-all-terms.txt, which is
deny-by-default: a term earns a place only when nearly all of its occurrences
really are the technical sense.  Within an eligible term, an occurrence is
skipped when it falls in maths, in a comment, inside a macro argument that must
stay literal, inside markup we already added, or when it matches one of the
veto patterns below -- the everyday readings that would otherwise be linked
wrongly.
"""
import re
import sys
import shutil
import pathlib

# Directories holding content modules.  Keep in step with tools/check_manuscript.pl.
CONTENT = ('tex/results', 'tex/routes', 'tex/archive')

# Regions that must never be touched.
BLOCKERS = [
    re.compile(r'(?m)(?<!\\)%.*$'),
    re.compile(r'\\(?:label|ref|eqref|pageref|hyperref|input|cite)\{[^}]*\}'),
    re.compile(r'\\(?:section|subsection|subsubsection|part)\*?\{[^}]*\}'),
    re.compile(r'\\(?:begin|end)\{[^}]*\}'),
    re.compile(r'\\(?:dfn|term)as\{[^}]*\}\{[^}]*\}'),
    re.compile(r'\\(?:dfn|term)x?\{[^}]*\}(?:\{[^}]*\})?'),
    re.compile(r'\$[^$]*\$'),
    re.compile(r'(?s)\\\[.*?\\\]'),
    re.compile(r'(?s)\\begin\{verbatim\}.*?\\end\{verbatim\}'),
]

# Everyday readings of eligible terms.  Add a pattern when a linked occurrence
# turns out to be the ordinary English word; a term needing many of these
# belongs in neither list, and should keep the one-link-per-module treatment.
VETO = re.compile(
    r'(?i)'
    r'goldbach\s+conjectured'          # the man, not the notion
)


def load_terms(path='tools/link-all-terms.txt'):
    terms = {}
    for line in pathlib.Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or ':' not in line:
            continue
        key, forms = line.split(':', 1)
        forms = [f.strip() for f in forms.split(',') if f.strip()]
        if forms:
            terms[key.strip()] = sorted(forms, key=len, reverse=True)
    return terms


def blocked_spans(text):
    spans = []
    for pat in BLOCKERS:
        spans += [m.span() for m in pat.finditer(text)]
    return spans


def covered(i, j, spans):
    return any(a <= i and j <= b for a, b in spans)


def mark(text, terms):
    """Wrap every eligible occurrence, longest form first, without overlaps."""
    spans = blocked_spans(text)
    taken, edits = [], []
    for key, forms in terms.items():
        pat = re.compile('|'.join(r'(?<![-\w])' + re.escape(f).replace(r'\ ', r'\s+')
                                  + r'(?![-\w])' for f in forms))
        for m in pat.finditer(text):
            i, j = m.span()
            if covered(i, j, spans) or any(a < j and i < b for a, b in taken):
                continue
            if VETO.search(text[max(0, i - 30):j + 20]):
                continue
            taken.append((i, j))
            surface = ' '.join(m.group(0).split())
            edits.append((i, j, '\\termx{%s}{%s}' % (key, surface)))
    for i, j, rep in sorted(edits, reverse=True):
        text = text[:i] + rep + text[j:]
    return text, len(edits)


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'build/linked-src')
    terms = load_terms()
    if (out / 'tex').exists():
        shutil.rmtree(out / 'tex')
    shutil.copytree('tex', out / 'tex')

    total = 0
    for d in CONTENT:
        for src in sorted(pathlib.Path(d).glob('*.tex')):
            text, n = mark(src.read_text(), terms)
            (out / src).write_text(text)
            total += n
    print(f'{len(terms)} eligible terms; {total} \\termx marks written to {out}/tex')


if __name__ == '__main__':
    main()
