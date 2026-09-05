# A conjecture, and the record of an attempt on it

A repository skeleton for a long-running proof search — the kind of project
that runs for months, is worked on largely by AI agents under human
supervision, and whose value lies as much in what it records about failed
approaches as in what it proves.

It gives you four things, wired together:

| | |
| --- | --- |
| `tex/` | a **three-edition manuscript** — established results, live routes, and a full working record — built into six PDFs with cross-document links |
| `tools/` | a **computational toolkit** (C++ and Python) with a rule that every computational claim names its program, its command, and its log |
| `formal/` | a **Lean 4 / mathlib** development with a blueprint mapping every manuscript label to its formal counterpart |
| `notes/` | the **agent's memory**, mirrored into the repository: one dead end per file |

and, holding them together, `make check`: a set of consistency checks that fail
the build when the record and the mathematics drift apart.

<!-- TEMPLATE-NOTE-START -->
## About this template

This repository is a scaffold, not a project.  It ships with a small worked
example — a fragment of the Goldbach conjecture — so that `make all` passes on
a fresh clone and every convention has a live instance you can copy.  Running
`make init` replaces the example with stubs and renames the project to yours.

The example is deliberately shallow mathematics.  What it demonstrates is the
*shape*: a proved lemma in the results edition, an open programme in the routes
companion, a refuted strengthening kept and marked closed, a superseded proof
in the archive, a computation with a retained log, a Lean theorem tied to a
manuscript label, and a note explaining what the refutation rules out.
<!-- TEMPLATE-NOTE-END -->

## Start here

```sh
git clone <this repo> MyConjecture && cd MyConjecture
make init                      # name the project; replaces the worked example
make all                       # six PDFs, then every consistency check
```

`make init` asks for a project name, a title and authors, and rewrites three
placeholder tokens through the whole tree:

| token | becomes | appears as |
| --- | --- | --- |
| `SCAFFOLD` | `KAKEYA` | LaTeX macro prefix, `\KAKEYAResultsView` |
| `Scaffold` | `Kakeya` | Lean namespace and library, `formal/Kakeya/` |
| `scaffold` | `kakeya` | file and PDF names, `tex/editions/kakeya-results.tex` |

It can also be driven non-interactively:

```sh
python3 tools/init_project.py --name Kakeya \
    --title "The Kakeya conjecture" --authors "A. Author" [--keep-example]
```

After it runs it is inert; the example remains in the git history.

## What you need

`make all` needs **LaTeX** (`latexmk` and a TeX Live installation with
`hyperref`, `xr-hyper`, `showkeys`, `longtable`), **Perl**, and **Python 3**.
Nothing else, and no Python packages.

```sh
sudo apt install texlive-latex-recommended texlive-latex-extra \
                 texlive-fonts-recommended latexmk        # Debian/Ubuntu
```

`make tools` needs a C++17 compiler.

**Lean is opt-in.**  `formal/` and `lakefile.lean` are ready to use, but
nothing in the default build touches them, because a first `lake build` pulls
several gigabytes of mathlib.  When you want it:

```sh
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh   # once, installs elan
lake exe cache get                                       # prebuilt mathlib
make formal                                              # lake build
```

Then set the repository variable `ENABLE_LEAN` to `true` to turn on the CI job
for it.  Bump `lean-toolchain` and the mathlib tag in `lakefile.lean` together,
never one alone.

## How the project is meant to be run

Read [`MANUSCRIPT.md`](MANUSCRIPT.md).  It is the contract: what the three
editions are for, where a given update belongs, what "proved" means here, and
how terminology is kept honest.  It is short, and everything else assumes it.

Then read [`AGENTS.md`](AGENTS.md) — the operating instructions for an agent
working in the repository, and equally a statement of what you should expect
one to do.  `CLAUDE.md` imports it, so Claude Code picks it up automatically;
point other tools at `AGENTS.md` directly.

The one-paragraph version:

* A statement with a complete proof goes in `tex/results/`.  A target you
  believe goes in `tex/routes/`, as a `prob`, never as a theorem with a gap.
* A refuted route stays in `tex/routes/`, marked closed, with its
  counterexample — deleting it guarantees someone tries it again.
* Status is asserted in exactly one place: the table in
  `tex/routes/00-status-map.tex`.
* A computational claim names its program, its exact command, and its retained
  log, and the program exits non-zero on failure.
* `make all` must pass before the work is done.

## The build

```sh
make all       # all six PDFs, then the reference, ownership and glossary checks
make results   # both variants of one edition
make check     # the checks alone (needs the PDFs)
make tools     # build the C++ toolkit
make audit     # the fast computational self-checks
make formal    # lake build (opt-in, see above)
make clean
```

The six PDFs land in `output/pdf/plain/` and `output/pdf/linked/`, which are
build products and are not tracked; `output/standalone/` is tracked, and is
where a PDF you intend to send to a person belongs.

`make check` is where most of the value is.  It fails the build when a label is
duplicated or dangling, when the results edition comes to depend on the
companion, when a module is missing from the full manifest, when a glossary row
has no definition or a definition has no row, when a term is linked from an
edition its row is gated out of, and when a newly emphasised word is neither
defined nor acknowledged as local.  Each of those checks exists because the
corresponding mistake is easy to make and expensive to find later.

## Layout

```
MANUSCRIPT.md        the workflow contract — read this first
AGENTS.md            operating instructions for AI agents (CLAUDE.md imports it)
Makefile             everything is a make target

tex/
  editions/          the six entry points; nothing else is a manuscript
  document.tex       the shared body: frontmatter, glossary, manifest
  preamble.tex       theorem environments, project notation, \dfn/\term macros
  glossary.tex       single source of truth for terminology
  manifests/         which modules each edition contains
  results/           proved statements and their proofs
  routes/            live targets, partial machinery, and closed routes
  archive/           superseded proofs and historical records
  standalone/        self-contained documents that are not views of the paper

tools/
  check_manuscript.pl   the consistency checks
  cpp/, python/         the toolkit; logs/ retains what the paper cites
  init_project.py       one-time project naming

formal/
  BLUEPRINT.md       manuscript label -> Lean name, with coverage and deviations
  Scaffold/          Basic, Results/, and a Tests/ module per result

notes/               mirrored agent memory: one dead end per file
```

## Continuous integration

`.github/workflows/ci.yml` builds the manuscript, runs `make check`, and runs
`make audit`, on every push.  The Lean job is skipped unless the repository
variable `ENABLE_LEAN` is `true`.
