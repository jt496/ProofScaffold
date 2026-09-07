# A conjecture, and the record of an attempt on it

A repository skeleton for a long-running proof search — the kind of project
that runs for months, is worked on largely by AI agents under human
supervision, and whose value lies as much in what it records about failed
approaches as in what it proves.

It gives you three things, wired together:

| | |
| --- | --- |
| `tex/` | a **three-edition manuscript** — established results, live routes, and a full working record — built into six PDFs with cross-document links |
| `tools/` | a **computational toolkit** (C++ and Python) with a rule that every computational claim names its program, its command, and its log |
| `formal/` | a **Lean 4 / mathlib** development with a blueprint mapping every manuscript label to its formal counterpart |

and, holding them together, `make check`: source and build checks for labels,
edition ownership, glossary links, and generated outputs. These checks do not
validate mathematical proofs; their exact scope is in [tools/VALIDATION.md](tools/VALIDATION.md).

There is deliberately **no notes or scratch directory**. The manuscript is the
single source of truth: a fact worth keeping is written into `tex/`, where the
checks can see it and a reader can find it. A parallel notes store starts as a
convenience and ends as a lagging copy that quietly contradicts the paper.

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

Start from the template, so that `origin` is your own repository from the very
first commit:

```sh
gh repo create MyConjecture --private --template jt496/ProofScaffold
git clone https://github.com/<you>/MyConjecture && cd MyConjecture
make init      # name the project; replaces the worked example
make all       # six PDFs, then every consistency check
```

GitHub's **Use this template** button does the same thing.

**Do not just clone this repository and start work in it.**  A clone leaves
`origin` pointing here, so the first `git push` of your new project lands on
the scaffold instead of on your own repository — and because `AGENTS.md` tells
an agent to commit and push as it goes, that push may well happen before you
have looked at the remote.  If you have already cloned directly, `make init`
removes the `origin` remote for you and says so; add your own before pushing.

`make init` also sets `core.hooksPath` to `.githooks`, which activates the hook
that refuses a push whose tree does not build.  That setting is per clone and
is not itself cloned, so a later clone of your project needs it again.

One thing to keep in mind as the project grows: this README should describe the
*shape* of the repository, not the *state* of the work.  Resist putting a list
of what is proved, or a count of open routes, at the top of it — that is a
second account of something the route table already maintains, and it is always
the stale copy that a newcomer reads first.

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
`hyperref`, `xr-hyper`, `showkeys`, `longtable`), **Perl**, **Python 3.10+**,
**Bash**, **Git**, and **Make**. No third-party Python packages are required.
The Git and Bash requirements support the tooling regression tests included
in `make all`.

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
for it.  Note that `AGENTS.md` tells an agent to ask before formalising
anything new, and to propose candidates rather than pick them: formalisation
is the most expensive thing in the project, and what is worth that cost is
your decision.  Bump `lean-toolchain` and the mathlib tag in `lakefile.lean` together,
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
make all       # all six PDFs, source/log checks and tooling regression tests
make results   # both variants of one edition
make check     # source and LaTeX log checks (needs the PDFs)
make check-source  # source checks only; no TeX installation needed
make test      # adversarial tooling regressions; no TeX or Lean needed
make tools     # build the C++ toolkit
make audit     # the fast computational self-checks
make smoke     # explicit alias for that subset, not full claim reproduction
make formal    # lake build (opt-in, see above)
make clean
```

The six PDFs land in `output/pdf/plain/` and `output/pdf/linked/`, which are
build products and are not tracked; `output/standalone/` is tracked, and is
where a PDF you intend to send to a person belongs.

`make check` is where most of the value is.  It fails the build when a label is
duplicated or dangling, when the results edition comes to depend on the
companion, when a module is missing or has the wrong edition ownership in a
manifest, when a glossary row has no definition or a definition has no row,
when a term is linked from an edition its row is gated out of, and when a newly
emphasised word is neither defined nor acknowledged as local. Each of those
checks exists because the corresponding mistake is easy to make and expensive
to find later.

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
  check_manuscript.pl   compatibility entry point for the source checker
  cpp/, python/         the toolkit; logs/ retains what the paper cites
  tests/                adversarial tooling regression fixtures
  VALIDATION.md         guarantees, supported syntax and limitations
  init_project.py       one-time project naming

formal/
  BLUEPRINT.md       manuscript label -> Lean name, with coverage and deviations
  Scaffold/          Basic, Results/, and a Tests/ module per result

```

## Local checks before a push

`.githooks/pre-push` refuses a push whose tree does not build.  `make init`
activates it, but the setting is local to a clone and is not itself cloned, so
every later clone of your project has to repeat it:

```sh
git config core.hooksPath .githooks
```

It lives in a tracked directory because `.git/hooks` is not cloned. Each distinct
pushed commit tip is built in a clean detached worktree, including non-current
branches and annotated tags. Uncommitted changes cannot make a broken commit
pass. This may rebuild all outputs rather than reuse the local build directory.

The hook is a local guard, not receiving-side enforcement. Bypass it deliberately
with `git push --no-verify`. It validates pushed tips, not every intermediate
commit. See [tools/VALIDATION.md](tools/VALIDATION.md) for limits and supported syntax.

## Continuous integration

`.github/workflows/ci.yml` runs cheap source checks and tooling regression tests
on both public and private repositories. Private runs allocate a runner and may
consume Actions minutes.

The more expensive manuscript and computational-audit jobs run automatically on
public repositories. For private repositories, trigger a run manually or set
`ENABLE_CI=true` under the repository's Actions variables. The Lean job additionally
requires `ENABLE_LEAN=true`. The workflow uses read-only repository permissions.

`make audit` (also named `make smoke`) runs the configured fast computational
subset. It is not full reproduction of every retained claim. Use a claim's exact
recorded command and domain for that. A successful build does not establish
proof correctness, experiment provenance, or that a formal statement faithfully
represents the manuscript.

## License

MIT — see [`LICENSE`](LICENSE).

That covers the scaffold: the build system, the checks, the toolkit skeleton
and the documentation. If you start a project from this template, the
mathematics you then write is yours, and you should put your own name on it —
edit the copyright line in `LICENSE`, or replace the file with whatever licence
you want your project under.
