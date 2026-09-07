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
import os
import tempfile
from tex_source import TexError, link_blockers
# Directories holding content modules.  Keep in step with tools/check_manuscript.pl.
CONTENT = ('tex/results', 'tex/routes', 'tex/archive')
# Everyday readings of eligible terms.  Add a pattern when a linked occurrence
# turns out to be the ordinary English word; a term needing many of these
# belongs in neither list, and should keep the one-link-per-module treatment.
VETO = re.compile(
    r'(?i)'
    r'goldbach\s+conjectured'          # the man, not the notion
)


def load_terms(path='tools/link-all-terms.txt'):
    terms = {}
    for line in pathlib.Path(path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or ':' not in line:
            continue
        key, forms = line.split(':', 1)
        forms = [f.strip() for f in forms.split(',') if f.strip()]
        if forms:
            terms[key.strip()] = sorted(forms, key=len, reverse=True)
    return terms

def blocked_spans(text):
    return link_blockers(text)


def covered(i, j, spans):
    # A match straddling a protected region is unsafe too.
    return any(a < j and i < b for a, b in spans)


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
            surface = m.group(0)  # preserve original whitespace exactly
            edits.append((i, j, '\\termx{%s}{%s}' % (key, surface)))
    for i, j, rep in sorted(edits, reverse=True):
        text = text[:i] + rep + text[j:]
    return text, len(edits)

def generate(out, root=pathlib.Path('.')):
    """Stage completely before replacing generated output; never delete sources.

    An existing output tree must be ours (marked), or the legacy default build
    tree. Custom unmarked directories and symlinks are refused, not removed.
    """
    root = root.resolve()
    source = root / 'tex'
    out = pathlib.Path(out).absolute()
    target = out / 'tex'
    resolved = target.resolve()
    if resolved == source or source in resolved.parents or resolved in source.parents:
        raise ValueError('output overlaps the source tex tree')
    # Symlink aliases can otherwise turn a harmless-looking path destructive.
    for path in (out, *out.parents, target):
        if path.is_symlink():
            raise ValueError(f'refusing symlink output path: {path}')
    marker = target / '.proof-linked-tree'
    legacy = target == root / 'build' / 'linked-src' / 'tex'
    if target.exists() and not target.is_dir():
        raise ValueError('output tex path is not a directory')
    if target.exists() and not marker.is_file() and not legacy:
        raise ValueError('refusing to replace an unmarked custom output tree')
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('source tex tree must not contain symlinks')
    terms = load_terms(root / 'tools' / 'link-all-terms.txt')
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    # A sibling staging directory keeps rename operations on one filesystem.
    with tempfile.TemporaryDirectory(prefix='.link-stage-', dir=out) as temporary:
        stage = pathlib.Path(temporary) / 'tex'
        shutil.copytree(source, stage)
        for directory in CONTENT:
            for src in sorted((root / directory).rglob('*.tex')):
                text, count = mark(src.read_text(encoding='utf-8'), terms)
                (stage / src.relative_to(source)).write_text(text, encoding='utf-8')
                total += count
        (stage / '.proof-linked-tree').write_text('Generated by link_all.py\n',
                                                 encoding='utf-8')
        backup = pathlib.Path(temporary) / 'previous'
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(stage, target)
        except BaseException:
            if backup.exists():
                os.replace(backup, target)
            raise
    return len(terms), total


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'build/linked-src')
    try:
        terms, total = generate(out)
    except (OSError, ValueError, TexError) as error:
        print(f'link_all: {error}', file=sys.stderr)
        return 1
    print(f'{terms} eligible terms; {total} \\termx marks written to {out}/tex')
    return 0


if __name__ == '__main__':
    sys.exit(main())
