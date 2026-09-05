#!/usr/bin/env python3
r"""Find project-coined vocabulary that the manuscript never defines.

Run from the repository root:

    python3 tools/python/undefined_terms.py

Prints candidate terms with their weight (how many modules use them, and how
often) and where they occur.  Terms carrying a glossary row, listed in
tools/local-terms.txt, or already reviewed and recorded in
tools/terms-reviewed.txt are excluded, so a run reports vocabulary coined since
the last pass.

`make check` cannot do this job: it only sees terms that were emphasised in the
first place.  This sweep finds the ones that were not -- coined compounds, and
modifiers of the project's own nouns, that no sentence in any edition defines.

It produces *candidates*, not a verdict.  The definitional-frame test below has
false positives -- "Let (p,q) be a Goldbach pair, so ..." matches the frame
while defining nothing -- so read the matches.  Either give a survivor a
glossary row, or record the judgement in tools/terms-reviewed.txt.

Three things it cannot see: a term defined too far from its first use, since
only terms with no definition at all surface; an ordinary word pressed into
technical service; and notation, permanently, since a symbol has nowhere to
carry a \dfn.
"""
import re
import glob
import pathlib
import collections

RESULTS   = sorted(glob.glob('tex/results/*.tex'))
COMPANION = sorted(glob.glob('tex/routes/*.tex') + glob.glob('tex/archive/*.tex'))

# --- project configuration -------------------------------------------------
# Nouns this project owns.  A modifier attached to one of them is usually
# coined vocabulary rather than ordinary English.  Extend as the project grows;
# this list is the main thing that makes the sweep sensitive.
NOUNS = ('pair', 'pairs', 'count', 'counts', 'prime', 'primes', 'number',
         'numbers', 'sieve', 'sieves', 'bound', 'bounds', 'range', 'ranges',
         'sum', 'sums', 'representation', 'representations', 'residue',
         'residues', 'interval', 'intervals', 'density', 'densities')
# ---------------------------------------------------------------------------

ORDINARY = set('''new old other same each such this that these those first second third
last one two three four five six seven eight nine ten every all any some both no more
most least many few single double whole entire full empty large small long short given
fixed chosen above below left right upper lower inner outer main only remaining resulting
following corresponding original present possible general particular arbitrary distinct
different equal common total final actual real complex finite infinite nonempty maximal
minimal proper improper unique disjoint parallel adjacent incident connected induced
ordered unordered directed undirected simple multiple its their our the a an of in for to
by with on at from is are be been was were has have had can could may might will would
shall should must does do did not and or if then so as it they we you'''.split())

# Sentence shapes in which a term is being introduced rather than merely used.
FRAMES = [
    r'\\emph\{[^{}]*%s[^{}]*\}',
    r'\\dfn(?:as)?\{[^{}]*\}?\{?[^{}]*%s',
    r'[Cc]all(?:ed)?\b[^.]{0,100}?%s',
    r'%s[^.]{0,60}?\bis called\b',
    r'\b(?:we say|say that)\b[^.]{0,100}?%s',
    r'\b(?:define|defines|defined|denote|denotes|denoted)\b[^.]{0,100}?%s',
    r'\b(?:write|writes)\b[^.]{0,60}?\bfor\b[^.]{0,60}?%s',
    r'\bby an?\b[^.]{0,40}?%s[^.]{0,20}?\bwe mean\b',
    r'%s\b[^.]{0,30}?\b(?:is|are|means)\b[^.]{0,20}?\bthe\b',
    r'\bLet\b[^.]{0,60}?\bbe (?:the|an?)\b[^.]{0,40}?%s',
    r'%s\b\s*,?\s*(?:that is|i\.e\.|namely)',
]


def strip_comments(text):
    return re.sub(r'(?m)(?<!\\)%.*$', '', text)


def prose(text):
    """Drop maths and macros, leaving the running text."""
    text = re.sub(r'(?s)\\\[.*?\\\]', ' ', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\(?:label|ref|eqref|cite|input)\{[^}]*\}', ' ', text)
    text = re.sub(r'\\(?:begin|end)\{[^}]*\}', ' ', text)
    return re.sub(r'\\[A-Za-z@]+', ' ', text)


def documented():
    """Keys and printed forms already in the glossary, plus the two lists."""
    gl = pathlib.Path('tex/glossary.tex').read_text()
    known = set(re.findall(r'\\gkeyx?\{([^}]+)\}', gl))
    known |= {re.sub(r'[\\${}]', '', m).strip().lower()
              for m in re.findall(r'\\gkeyx?\{[^}]+\}\{([^}]+)\}', gl)}
    for name in ('tools/local-terms.txt', 'tools/terms-reviewed.txt'):
        for line in pathlib.Path(name).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                known.add(line.lower())
    return known


def main():
    raw  = {f: strip_comments(pathlib.Path(f).read_text()) for f in RESULTS + COMPANION}
    text = {f: prose(v) for f, v in raw.items()}
    known = documented()

    hyphenated = re.compile(r"(?<![-\w])([a-z][a-z]*(?:-[a-z]+)+)(?![-\w])")
    modified   = re.compile(r"(?<![-\w])([A-Za-z][A-Za-z-]{2,})\s+(%s)(?![-\w])"
                            % '|'.join(NOUNS))

    cand = collections.defaultdict(set)
    for f, t in text.items():
        for m in hyphenated.finditer(t):
            w = m.group(1).lower()
            if len(w.split('-')) == 2 and w.split('-')[0] in ORDINARY:
                continue
            cand[w].add(f)
        for m in modified.finditer(t):
            if m.group(1).lower() in ORDINARY:
                continue
            cand[f'{m.group(1).lower()} {m.group(2).lower()}'].add(f)

    def defined(term):
        e = re.escape(term).replace(r'\ ', r'\s+')
        return any(re.compile(fr % e, re.I | re.S).search(v)
                   for fr in FRAMES for v in raw.values())

    def count(term, files):
        p = re.compile(r'(?<![-\w])' + re.escape(term).replace(r'\ ', r'\s+')
                       + r'(?![-\w])', re.I)
        return sum(len(p.findall(text[f])) for f in files)

    rows = []
    for term, files in cand.items():
        if term in known or len(files) < 2:
            continue
        n = count(term, text)
        if n < 4 or defined(term):
            continue
        rows.append((len(files), n, term, sorted(files)))
    rows.sort(key=lambda r: (-r[0], -r[1]))

    print(f'{len(rows)} candidate terms with no definitional frame\n')
    print(f'{"mod":>4} {"uses":>5}  {"term":<34} {"results?":<9} where')
    for nfiles, n, term, where in rows:
        in_results = any(f in RESULTS for f in where)
        names = ', '.join(pathlib.Path(f).stem[:24] for f in where[:3])
        if len(where) > 3:
            names += f' +{len(where) - 3}'
        print(f'{nfiles:>4} {n:>5}  {term:<34} {"YES" if in_results else "-":<9} {names}')


if __name__ == '__main__':
    main()
