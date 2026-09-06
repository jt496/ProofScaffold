#!/usr/bin/env python3
"""Turn this scaffold into your project.

    make init                                   # interactive
    python3 tools/init_project.py --name Kakeya --title "The Kakeya conjecture" \
        --authors "A. Author and B. Author"

Three placeholder tokens run through the whole repository and are rewritten
together:

    SCAFFOLD    LaTeX macro prefix        \\SCAFFOLDResultsView
    Scaffold    Lean namespace and lib    formal/Scaffold/, namespace Scaffold
    scaffold    file and PDF name slug    tex/editions/scaffold-results.tex

Giving --name Kakeya sets them to KAKEYA / Kakeya / kakeya; override any of
them individually with --upper, --camel, --slug.  The name must be letters
only, because a LaTeX macro name cannot contain digits.

By default the worked Goldbach example is replaced by minimal stubs that still
build green, so that `make all` passes immediately on your empty project.  Pass
--keep-example to keep it; it is in the git history either way.
"""
import argparse
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', 'build', 'output', '.lake', '__pycache__', 'tmp'}
# This script names the placeholders in its own source, so it is never a
# subject of the rewrite it performs.
SKIP_FILES = {'tools/init_project.py'}
TEXTUAL = {'.tex', '.md', '.py', '.pl', '.lean', '.yml', '.yaml', '.json',
           '.txt', '.cpp', '.hpp', '.log', '.toml', '.cfg', ''}
TOKENS = ('SCAFFOLD', 'Scaffold', 'scaffold')


# ---------------------------------------------------------------------------
# Stub content used when the worked example is stripped.  Every stub is chosen
# so that `make all` still passes: the checks in tools/check_manuscript.pl are
# unforgiving, and a scaffold whose first build is red is worse than useless.
# ---------------------------------------------------------------------------
STUBS = {
'tex/results/00-introduction.tex': r"""\section{Introduction}\label{sec:intro}

This project is an attempt on the following.

\begin{conjecture}[@@NAME@@]\label{main:conj}
@@CONJECTURE@@
\end{conjecture}

\begin{definition}\label{object:def}
The central object is a \dfn{widget}: replace this with the definition your
conjecture is about, and rename the glossary row in \texttt{tex/glossary.tex}
to match.
\end{definition}

Say here what this edition establishes, and point at the companion for what is
open.  Keep it short: the route table in the companion is the maintained
account of status, and repeating it here guarantees one of the two goes stale.
""",
'tex/routes/00-status-map.tex': r"""\section{Current status and route map}\label{sec:status}

This table is the maintained route index, and the only place in the project
where the status of a programme is asserted.  ``Open'' means the displayed
target is sufficient but unproved; ``closed'' means an exact counterexample to
it is recorded in this companion.

\begingroup
\small
\renewcommand{\arraystretch}{1.12}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.22\textwidth}
                       >{\raggedright\arraybackslash}p{0.48\textwidth}
                       >{\raggedright\arraybackslash}p{0.18\textwidth}@{}}
\textbf{Programme} & \textbf{Current target} & \textbf{State}\\ \hline
\endfirsthead
\textbf{Programme} & \textbf{Current target} & \textbf{State}\\ \hline
\endhead
First route & Problem~\ref{first:prob}. & open; priority 1\\
\end{longtable}
\endgroup
""",
'tex/routes/10-first-route.tex': r"""\section{First route}\label{sec:first-route}

Describe the programme: what would be enough, and why it would be enough.  A
route module is worth writing even when the target is far off, because the
reduction itself is a result.

\begin{prob}\label{first:prob}
State the sufficient target here.  Use a \texttt{prob} environment, never a
theorem with a gap.
\end{prob}

A positive answer implies Conjecture~\ref{main:conj}, by \dots

Record here what is known about the target, what has been tried, and where the
argument currently stops.  The \term{widget} of Definition~\ref{object:def} is
linked on its first use in this module, and not again.
""",
'tex/glossary.tex': r"""% Shared reference sheet, included by all three editions.  Every row names a
% term or symbol, states what it means in one line, and points at the place
% where it is properly defined; that pointer is a live link, and in the
% companion editions it leads into the results PDF through xr-hyper.
%
% A row's first cell carries the anchor planted by the \gkey macro: writing
% \term with the same key in the body turns that occurrence into a link to this
% table.  Keep the rows in alphabetical order, and keep every \gkey key matched
% by exactly one \dfn in the body.
%
% A row whose pointer is a companion-owned label must be gated with
%   \ifdefined\SCAFFOLDResultsView\else ... \fi
% or the results edition fails on an undefined reference.  A gated row must not
% be linked from a results module; tools/check_manuscript.pl checks both.

\phantomsection
\section*{Terminology and notation}
\addcontentsline{toc}{section}{Terminology and notation}

Each entry below is defined once in the body, at the place named in the last
column; the definition there is the authoritative one, and what is recorded
here is only enough to read on with.  Terms set in blue elsewhere in the text
link to their row in the first table.

\subsection*{Terminology}

\begingroup
\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}
\renewcommand{\arraystretch}{1.25}
\begin{longtable}{@{}p{0.24\textwidth}p{0.505\textwidth}p{0.165\textwidth}@{}}
\hline
\textbf{Term} & \textbf{Meaning} & \textbf{Defined in}\\
\hline
\endhead
\hline
\endfoot

\gkey{widget}{widget} &
The central object.  Replace this row, and the \verb|\dfn| that matches it, as
soon as you know what your conjecture is about. &
Def.~\ref{object:def}\\

\end{longtable}
\endgroup

\subsection*{Notation}

\begingroup
\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}
\renewcommand{\arraystretch}{1.25}
\begin{longtable}{@{}p{0.24\textwidth}p{0.505\textwidth}p{0.165\textwidth}@{}}
\hline
\textbf{Symbol} & \textbf{Meaning} & \textbf{Defined in}\\
\hline
\endhead
\hline
\endfoot

$W$ & A widget.  Notation rows need no \verb|\dfn|; adding the row when you
add the notation is the one convention nothing can check for you. &
Def.~\ref{object:def}\\

\end{longtable}
\endgroup
""",
'tex/archive/40-computations.tex': r"""\section{Computational audit}\label{sec:computations}

The retained record of what was searched, over what range, with which program,
and what was found.  A negative finding belongs here even when --- especially
when --- it closed a route: the range over which something was checked is the
part a later argument needs, and the part that is easiest to lose.

Nothing has been computed yet.
""",
'tex/manifests/results.tex': r"""% Established mathematics only.  Each statement and proof is owned by exactly
% one module; the routes companion imports these labels through xr-hyper.
% Nothing in this manifest may refer to a route- or archive-owned label --
% tools/check_manuscript.pl enforces that.

\input{tex/results/00-introduction}
""",
'tex/manifests/routes.tex': r"""% The live companion: the status map first, then one module per programme.
% Route modules may refer freely to results-owned labels, which arrive through
% xr-hyper; the reverse direction is forbidden.

\part{Status}
\input{tex/routes/00-status-map}

\part{Open programmes}
\input{tex/routes/10-first-route}
""",
'tex/manifests/archive.tex': r"""% The full working edition.  This manifest must include every mathematical
% module in tex/results, tex/routes and tex/archive exactly once; adding a
% module anywhere without adding it here fails `make check`.

\input{tex/results/00-introduction}

\part{Status}
\input{tex/routes/00-status-map}

\part{Open programmes}
\input{tex/routes/10-first-route}

\appendix
\part{Archive}
\input{tex/archive/40-computations}
""",
'tex/frontmatter/results.tex': r"""\maketitle
% Keep this abstract in step with the mathematics.  It is one of the two
% maintained accounts of what is established -- summarise here what this
% edition proves, and update it when that changes.  It must not carry route
% status: no priorities, no counts, no "currently".  The route table owns that.
\begin{abstract}
@@CONJECTURE@@
This edition contains the established results and their proofs.  Open proof
programmes, failed strengthenings, and detailed computational audits are
maintained separately in the routes companion and the full working edition.
\end{abstract}
""",
'tex/frontmatter/routes.tex': r"""\maketitle
\begin{abstract}
@@CONJECTURE@@
This is the companion to the results edition: the maintained record of what is
being attempted and what has already failed.  Statements imported from the
results edition are linked into it, so a reference to an established result
opens the other document at the right page.  Nothing here is claimed as
proved; anything that becomes proved moves to the results edition.
\end{abstract}
""",
'tex/frontmatter/archive.tex': r"""\maketitle
\begin{abstract}
@@CONJECTURE@@
The complete working record: every established result with its proof, every
live route, and the archive of superseded proofs, refuted strengthenings and
negative examples.  This is the edition to search when asking whether something
has already been tried.
\end{abstract}
""",
'tex/preamble-notation': None,   # handled specially below
'tools/local-terms.txt': """# Emphasis that is deliberately not a glossary entry.
#
# tools/check_manuscript.pl requires every \\emph{...} in a content module to be
# either a \\dfn (a term with a row in tex/glossary.tex) or listed here.  That is
# what stops new terminology entering the manuscript undocumented: a new
# emphasised term fails the build until it is either given a glossary row or
# acknowledged below.
#
# Add a term here when it is confined to one module, so that its definition is
# always a few lines from every use.  Promote it to tex/glossary.tex when a
# second module starts using it.  Run-in headers (a capitalised phrase ending
# in a full stop) and \\emph containing \\ref are skipped automatically.
""",
'tools/link-all-terms.txt': """# Terms whose *every* occurrence may be linked, for the densely linked editions.
#
# tools/python/link_all.py reads this file and links only the terms listed
# here; everything else keeps the one-link-per-module treatment.  The list is
# deny-by-default on purpose: a term earns a place only when nearly every
# occurrence really is the technical sense.  Sample the occurrences before
# promoting one.
#
# Format:  key: printed form, other form, ...
# The key must have a glossary row (make check enforces this).

widget: widgets, widget
""",
'tools/cpp/core.hpp': """// ---------------------------------------------------------------------------
// Shared machinery for the C++ toolkit.  Every program in this directory
// includes this header, so that a decision about how the objects are
// represented is made once and named in tools/README.md, rather than made
// again in every program.
//
// Put the project's representation here.
// ---------------------------------------------------------------------------
#pragma once
#include <cstdint>
#include <cstdio>
#include <vector>
""",
'tools/cpp/example.cpp': """// Template for a program supporting a manuscript claim.
//
// The three requirements, from tools/README.md:
//   1. a final line that is either `ALL ... ASSERTIONS PASSED` or a failure,
//      and a non-zero exit status on failure, so CI can run it unattended;
//   2. deterministic, or an explicit seed argument;
//   3. named, with its exact arguments, in the statement it supports.
#include "core.hpp"
#include <cstdlib>

int main(int argc, char** argv) {
    long long n = (argc > 1) ? atoll(argv[1]) : 10;
    long long failures = 0;

    // ... the search ...
    printf("n=%lld  failures: %lld\\n", n, failures);

    printf(failures ? "EXAMPLE AUDIT FAILED\\n"
                    : "ALL EXAMPLE AUDIT ASSERTIONS PASSED\\n");
    return failures ? 1 : 0;
}
""",
}


def repo_files():
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.as_posix() in SKIP_FILES:
            continue
        yield path


def rewrite_tokens(mapping, dry):
    pattern = re.compile('|'.join(TOKENS))
    changed = 0
    for path in repo_files():
        if path.suffix not in TEXTUAL:
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        new = pattern.sub(lambda m: mapping[m.group(0)], text)
        if new != text:
            changed += 1
            if not dry:
                path.write_text(new)
    # Paths second, deepest first, so a renamed directory does not invalidate
    # the paths still queued behind it.
    renamed = 0
    for path in sorted(repo_files(), key=lambda p: -len(p.parts)):
        name = pattern.sub(lambda m: mapping[m.group(0)], path.name)
        if name != path.name:
            renamed += 1
            if not dry:
                path.rename(path.with_name(name))
    for path in sorted((p for p in ROOT.rglob('*') if p.is_dir()),
                       key=lambda p: -len(p.parts)):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        name = pattern.sub(lambda m: mapping[m.group(0)], path.name)
        if name != path.name:
            renamed += 1
            if not dry:
                path.rename(path.with_name(name))
    return changed, renamed


def set_metadata(title, authors, dry):
    p = ROOT / 'tex' / 'metadata.tex'
    text = ('% Set by `make init`, or edit by hand.\n'
            f'\\title{{{title}}}\n\\author{{{authors}}}\n')
    if not dry:
        p.write_text(text)


def strip_example(camel, dry, conjecture, name):
    """Replace the worked example with stubs that still build green.

    The conjecture is written into the introduction and into all three
    frontmatter abstracts, so that the editions describe the actual problem
    from the first build rather than carrying placeholder prose that nobody
    remembers to replace.
    """
    remove = [
        'tex/results/01-tools.tex',
        'tex/results/02-verification.tex',
        'tex/routes/10-density.tex',
        'tex/routes/20-distinct-primes.tex',
        'tex/archive/10-superseded-verification.tex',
        'tools/cpp/goldbach.cpp',
        'tools/python/distinct_goldbach.py',
        'tools/python/goldbach_counts.py',
        'tools/logs/goldbach-1e8.log',
        'tools/logs/distinct-primes-1e6.log',
        f'formal/{camel}/Basic.lean',
        f'formal/{camel}/Results/Goldbach.lean',
        f'formal/{camel}/Tests/Goldbach.lean',
    ]
    for rel in remove:
        p = ROOT / rel
        if p.exists() and not dry:
            p.unlink()

    for rel, body in STUBS.items():
        if body is None:
            continue
        p = ROOT / rel
        if not dry:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body.replace('@@CONJECTURE@@', conjecture)
                             .replace('@@NAME@@', name))

    if dry:
        return

    # Lean stubs.
    (ROOT / 'formal' / camel / 'Basic.lean').write_text(
        f"""import Mathlib

/-!
# Basic definitions

The definitions of `tex/results/00-introduction.tex`.  Every public name here
should carry a docstring naming its manuscript label, and appear in the
Coverage table of `formal/BLUEPRINT.md`.
-/

namespace {camel}

/-- Definition `object:def`.  Replace with the project's central object. -/
def Widget : Type := Unit

end {camel}
""")
    (ROOT / 'formal' / camel / 'Results').mkdir(parents=True, exist_ok=True)
    (ROOT / 'formal' / camel / 'Results' / 'Example.lean').write_text(
        f"""import {camel}.Basic

/-!
# First formalized result

One `Results/` module per manuscript module, named after it.
-/

namespace {camel}
namespace Results

/-- Replace with the first statement you formalize, and add its Coverage row
in `formal/BLUEPRINT.md` in the same commit. -/
theorem placeholder : True := trivial

end Results
end {camel}
""")
    (ROOT / 'formal' / camel / 'Tests').mkdir(parents=True, exist_ok=True)
    (ROOT / 'formal' / camel / 'Tests' / 'Example.lean').write_text(
        f"""import {camel}.Results.Example

/-!
# Regression tests

A `Tests/` module per `Results/` module.  Its job is to pin the *statements*:
if a definition is weakened or a hypothesis quietly added, the build breaks
here rather than silently in a downstream proof.  Tests prove nothing new.
-/

namespace {camel}
namespace Tests

example : True := Results.placeholder

end Tests
end {camel}
""")
    (ROOT / 'formal' / f'{camel}.lean').write_text(
        f"""-- Library root.  Every module in formal/{camel}/ is imported here, so that
-- `lake build` builds the whole development and nothing can be orphaned.
import {camel}.Basic
import {camel}.Results.Example
import {camel}.Tests.Example
""")

    # Blueprint: keep the conventions, empty the project-specific tables.
    bp = ROOT / 'formal' / 'BLUEPRINT.md'
    text = bp.read_text()
    text = re.sub(r'(?s)\n## Coverage\n.*?\n## Deviations\n.*?\n## Adding to this development',
                  """
## Coverage

Every labelled result of `tex/manifests/results.tex`, and what has become of
it.  Add a row when you formalize something, and add a row saying *open* or
*non-goal* when you decide not to.

| manuscript | statement | Lean | status |
| --- | --- | --- | --- |
| `main:conj` | the conjecture | — | open, obviously |

## Deviations

Departures from the manuscript, in full: statements proved in stronger or
weaker form, hypotheses that turned out to be unnecessary, proofs that take a
different route, and any error formalization uncovered in the paper.  Empty so
far.

## Adding to this development""", text)
    bp.write_text(text)

    # tools/README.md: keep the rules, empty the tables.
    (ROOT / 'tools' / 'README.md').write_text("""# Computational toolkit

Programs supporting the manuscript.  Everything a computational claim in the
paper rests on was produced here, and every such claim names the program, the
exact command, and the retained log.

Layout:

* `cpp/`    — exhaustive and large-scale searches (C++17).  `make` builds all.
* `python/` — exploratory scripts and small audits.  Standard library only.
* `logs/`   — retained output of the runs the manuscript cites.

## Conventions

`cpp/core.hpp` holds the shared representation, so that a decision about how
the objects are encoded is made once.  Document it here as a table of the
symbols it exports, so that a program can be read without reading the header.

A program that supports a manuscript claim must:

1. print a final line that is either `ALL ... ASSERTIONS PASSED` or a failure,
   and exit non-zero on failure, so it can be run in CI without a human
   reading the output;
2. be deterministic, or take an explicit seed;
3. be named, with its exact arguments, in the statement it supports.

`tools/cpp/example.cpp` is a template that meets all three.

## cpp/

| program | arguments | what it does |
| --- | --- | --- |
| `example` | `n` | template; replace it. |

## python/

| script | what it does |
| --- | --- |
| `link_all.py` | build-time: writes the marked-up copy of `tex/` for the densely linked editions.  Never edit its output. |
| `undefined_terms.py` | sweeps for coined vocabulary the manuscript never defines.  Produces candidates, not a verdict; see `MANUSCRIPT.md`. |

## Results reproduced

Every command a manuscript claim names, in one block, so the whole
computational record can be re-run:

```
make -C tools/cpp
tools/cpp/example 10
```

`make audit` runs the fast subset of these; CI runs the same target.
""")

    # The Makefile audit target names the example programs.
    mk = ROOT / 'Makefile'
    text = mk.read_text()
    text = re.sub(r'(?m)^audit: tools\n(?:\t.*\n)+',
                  'audit: tools\n\ttools/cpp/example 10\n', text)
    mk.write_text(text)

    # The Goldbach-specific notation block in the preamble.
    pre = ROOT / 'tex' / 'preamble.tex'
    text = pre.read_text()
    notation = (
        '% --- project notation '
        + '-' * 56 + '\n'
        '% Keep macros here rather than in the modules, so that a change of '
        'notation is\n% one edit and every edition agrees.\n'
        '\\newcommand{\\N}{\\mathbb{N}}\n'
        '\\newcommand{\\R}{\\mathbb{R}}\n'
        '% ' + '-' * 75 + '\n')
    text = re.sub(r'(?s)% --- project notation.*?% -{20,}\n',
                  lambda _m: notation, text)
    pre.write_text(text)

    (ROOT / 'tools' / 'logs' / '.gitkeep').touch()
    (ROOT / 'tex' / 'archive' / '.gitkeep').touch()


def strip_template_section():
    """Remove the 'About this template' block from README.md."""
    p = ROOT / 'README.md'
    if not p.exists():
        return
    text = p.read_text()
    text = re.sub(r'(?s)\n<!-- TEMPLATE-NOTE-START -->.*?<!-- TEMPLATE-NOTE-END -->\n',
                  '\n', text)
    p.write_text(text)


def ask(prompt, default=''):
    suffix = f' [{default}]' if default else ''
    try:
        got = input(f'{prompt}{suffix}: ').strip()
    except EOFError:
        got = ''
    return got or default


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', help='project name, letters only, e.g. Kakeya')
    ap.add_argument('--upper', help='override the LaTeX macro prefix')
    ap.add_argument('--camel', help='override the Lean namespace')
    ap.add_argument('--slug', help='override the file-name slug')
    ap.add_argument('--title', help='manuscript title')
    ap.add_argument('--authors', help='manuscript authors')
    ap.add_argument('--conjecture',
                    help='one-sentence statement of the problem; goes into the '
                         'introduction and all three abstracts')
    ap.add_argument('--keep-example', action='store_true',
                    help='keep the worked Goldbach example')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if 'SCAFFOLD' not in (ROOT / 'tex' / 'preamble.tex').read_text():
        print('This repository has already been initialised: no SCAFFOLD '
              'placeholders remain.\nNothing to do.')
        return 1

    name = args.name
    if not name and sys.stdin.isatty():
        print(__doc__.split('\n\n')[0])
        name = ask('Project name (letters only, e.g. Kakeya)')
    if not name:
        ap.error('--name is required')
    if not re.fullmatch(r'[A-Za-z]+', name):
        ap.error('the name must be letters only: it becomes a LaTeX macro '
                 'prefix, and a macro name cannot contain digits or hyphens')

    camel = args.camel or name[0].upper() + name[1:]
    upper = args.upper or name.upper()
    slug  = args.slug  or name.lower()

    title = args.title
    authors = args.authors
    conjecture = args.conjecture
    if sys.stdin.isatty():
        title = title or ask('Manuscript title', f'The {name} conjecture')
        authors = authors or ask('Authors', 'Your Name')
        conjecture = conjecture or ask('One-sentence statement of the problem')
    title = title or f'The {name} conjecture'
    authors = authors or 'Your Name'
    # A placeholder that still builds: no \emph, which make check would reject.
    conjecture = conjecture or 'State the problem here.'

    keep = args.keep_example
    if not keep and not args.name and sys.stdin.isatty():
        keep = ask('Keep the worked Goldbach example? (y/N)', 'N').lower().startswith('y')

    print(f'\n  SCAFFOLD -> {upper}\n  Scaffold -> {camel}\n  scaffold -> {slug}')
    print(f'  title    : {title}\n  authors  : {authors}')
    print(f'  example  : {"kept" if keep else "replaced by stubs"}')
    if not keep:
        print(f'  problem  : {conjecture}')
    elif args.conjecture:
        print('  note     : --conjecture is ignored with --keep-example, whose '
              'abstracts describe the worked example')
    print()
    if args.dry_run:
        print('(dry run: nothing written)')

    if not keep:
        strip_example(camel='Scaffold', dry=args.dry_run,
                      conjecture=conjecture, name=camel)
    set_metadata(title, authors, args.dry_run)
    changed, renamed = rewrite_tokens(
        {'SCAFFOLD': upper, 'Scaffold': camel, 'scaffold': slug}, args.dry_run)
    if not args.dry_run:
        strip_template_section()

    print(f'{changed} files rewritten, {renamed} paths renamed.')
    where = ('the worked example under tex/results/ and tex/routes/, which you '
             'can now\nedit or delete'
             if keep else
             'tex/results/00-introduction.tex, and put your first target in\n'
             'tex/routes/10-first-route.tex')
    print(f"""
Next:

    make all            # six PDFs and every check; should pass as-is
    git add -A && git commit -m 'Initialise {camel}'

Then read MANUSCRIPT.md, write your conjecture into {where}.

The LICENSE file still carries the scaffold author's copyright line; put your
own name on it, or replace the file, before the work is yours.""")
    return 0


if __name__ == '__main__':
    sys.exit(main())
