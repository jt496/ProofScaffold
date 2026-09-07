#!/usr/bin/env python3
"""Check literal manuscript structure, not mathematical correctness.

Run from the repository root. See tools/VALIDATION.md for the supported TeX
subset and the scope of the checks. No third-party Python packages are needed.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path, PurePosixPath
import re
import sys

from tex_source import TexError, commands, edition_text, group, mask, source_text

PREFIX = 'SCAFFOLD'
OWNERS = ('results', 'routes', 'archive')
REFERENCES = {'ref', 'eqref', 'pageref', 'autoref', 'nameref'}
IDENTIFIER = re.compile(r'[-A-Za-z0-9_:.+/]+\Z')
# Add an expression here when retiring a root-level entry point.
RETIRED: tuple[str, ...] = ()


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def argument(text: str, command) -> str:
    pos = command.end
    if pos < len(text) and text[pos] == '*':
        pos += 1
    value, _ = group(text, pos)
    return value


def keys(text: str, names: set[str]):
    for command in commands(text):
        if command.name in names:
            value = argument(text, command)
            if not IDENTIFIER.fullmatch(value):
                raise TexError(f'\\{command.name} needs a literal identifier, got {value!r}')
            yield command.name, value


def manifest(path: Path, expected: set[str], content: set[str]) -> None:
    """Only direct module inputs, part headings, and layout commands are allowed.

    Indirection and arbitrary macro expansion would require a TeX interpreter;
    reject them instead of claiming that an incomplete scan was successful.
    """
    text = edition_text(source_text(read(path)), path.stem == 'results', PREFIX)
    spans, inputs = [], []
    end = 0
    for command in commands(text):
        if command.start < end:
            continue
        pos = command.end
        if command.name in {'input', 'part'}:
            if command.name == 'part' and text[pos:pos + 1] == '*':
                pos += 1
            value, end = group(text, pos)
            if command.name == 'input':
                if '\\' in value or '%' in value or any(ch.isspace() for ch in value):
                    raise TexError(f'{path}: input must be a literal module path')
                value = value if value.endswith('.tex') else value + '.tex'
                parts = PurePosixPath(value).parts
                if '..' in parts or not value.startswith('tex/'):
                    raise TexError(f'{path}: unsupported module path {value}')
                if value not in content:
                    raise TexError(f'{path}: missing or non-content input {value}')
                inputs.append(value)
        elif command.name in {'appendix', 'clearpage', 'newpage'}:
            end = pos
        else:
            raise TexError(f'{path}: unsupported manifest command \\{command.name}')
        spans.append((command.start, end))
    if mask(text, spans).strip():
        raise TexError(f'{path}: unexpected manifest text (only direct inputs and headings allowed)')
    counts = Counter(inputs)
    for value in sorted(set(counts) | expected):
        wanted = 1 if value in expected else 0
        if counts[value] != wanted:
            raise TexError(f'{path}: includes {value} {counts[value]} times '
                           f'(expected {wanted}; check edition ownership)')


def check(root: Path = Path('.')) -> str:
    for item in root.iterdir():
        if any(re.search(pattern, item.name) for pattern in RETIRED):
            raise TexError(f'retired manuscript entry point: {item.name}')
    content = sorted(path for owner in OWNERS
                     for path in (root / 'tex' / owner).rglob('*.tex'))
    if not content:
        raise TexError('no content modules found; run from the repository root')
    paths = {path.relative_to(root).as_posix(): path for path in content}
    texts = {name: source_text(read(path)) for name, path in paths.items()}
    # Validate the conditional subset before using either reader view.
    views = {(name, results): edition_text(text, results, PREFIX)
             for name, text in texts.items() for results in (True, False)}
    labels: dict[str, str] = {}
    definitions: dict[str, str] = {}
    for name, text in texts.items():
        for _, label in keys(text, {'label'}):
            if label in labels:
                raise TexError(f'duplicate label {label} in {labels[label]} and {name}')
            labels[label] = name
        for _, key in keys(text, {'dfn', 'dfnas'}):
            if key in definitions:
                raise TexError(f'term {key} defined twice: {definitions[key]} and {name}')
            definitions[key] = name
    all_paths = set(paths)
    for view, owned in [('results', {'results'}), ('routes', {'routes'}),
                        ('archive', set(OWNERS))]:
        expected = {name for name in paths if name.split('/')[1] in owned}
        manifest(root / 'tex' / 'manifests' / f'{view}.tex', expected, all_paths)

    gloss = source_text(read(root / 'tex' / 'glossary.tex'))
    rows: dict[str, str] = {}
    for kind, key in keys(gloss, {'gkey', 'gkeyx'}):
        if key in rows:
            raise TexError(f'duplicate glossary row {key}')
        rows[key] = kind
    row_views = {results: {key for _, key in keys(edition_text(gloss, results, PREFIX),
                                                {'gkey', 'gkeyx'})}
                 for results in (True, False)}
    for key, kind in rows.items():
        if kind == 'gkey' and key not in definitions:
            raise TexError(f'glossary row {key} has no \\dfn; add one or use \\gkeyx')
        if kind == 'gkeyx' and key in definitions:
            raise TexError(f'glossary row {key} is \\gkeyx but {definitions[key]} defines it')
    for key, name in definitions.items():
        if key not in rows:
            raise TexError(f'\\dfn{{{key}}} in {name} has no glossary row')

    def references(text: str, name: str, results: bool) -> None:
        for _, label in keys(text, REFERENCES):
            if label not in labels:
                raise TexError(f'unknown label {label} referenced by {name}')
            if results and not labels[label].startswith('tex/results/'):
                raise TexError(f'results-to-companion dependency: {name} -> '
                               f'{label} ({labels[label]})')

    links = set()
    for name in paths:
        for results in (True, False):
            if results and not name.startswith('tex/results/'):
                continue
            text = views[name, results]
            references(text, name, results)
            for _, key in keys(text, {'term', 'termas'}):
                if key not in row_views[results]:
                    raise TexError(f'\\term{{{key}}} in {name} has no visible glossary row '
                                   f'in {"results" if results else "companion/full"} view')
                links.add((name, key))
    for results in (True, False):
        references(edition_text(gloss, results, PREFIX), 'tex/glossary.tex', results)
    for view in ('results', 'routes', 'archive'):
        path = root / 'tex' / 'frontmatter' / f'{view}.tex'
        if path.exists():
            text = edition_text(source_text(read(path)), view == 'results', PREFIX)
            references(text, str(path), view == 'results')
            for _, key in keys(text, {'term', 'termas'}):
                if key not in row_views[view == 'results']:
                    raise TexError(f'{path}: term {key} has no visible glossary row')

    allowed = {line.strip() for line in read(root / 'tools' / 'local-terms.txt').splitlines()
               if line.strip() and not line.lstrip().startswith('#')}
    for name, text in texts.items():
        for command in commands(text):
            if command.name != 'emph':
                continue
            term = argument(text, command)
            if re.search(r'\\(?:ref|eqref|dfn|term)', term):
                continue
            if re.fullmatch(r'[A-Z].*\.', term, re.S):
                continue
            term = ' '.join(term.split())
            if term not in allowed:
                raise TexError(f'{name}: emphasised term {term!r} is neither a \\dfn '
                               'nor listed in tools/local-terms.txt')
    for line in read(root / 'tools' / 'link-all-terms.txt').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, separator, forms = line.partition(':')
        key = key.strip()
        if not separator or not forms.strip():
            raise TexError('malformed tools/link-all-terms.txt entry: ' + line)
        if key not in rows:
            raise TexError(f'link-all key {key!r} has no glossary row')
        # Generated links must not bypass the hand-authored visibility checks.
        if key not in row_views[True]:
            from link_all import mark
            terms = {key: [form.strip() for form in forms.split(',') if form.strip()]}
            for name, path in paths.items():
                if name.startswith('tex/results/'):
                    active = views[name, True]
                    _, count = mark(active, terms)
                    if count:
                        raise TexError(f'{name}: dense linking would target hidden glossary row {key}')
    return (f'{len(paths)} content modules; {len(labels)} unique labels; '
            f'{len(rows)} glossary rows; {len(links)} term links; '
            'all source, ownership and glossary checks pass')


def main() -> int:
    try:
        print(check())
    except (OSError, TexError) as error:
        print(f'manuscript check: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
