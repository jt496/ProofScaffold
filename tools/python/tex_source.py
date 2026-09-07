"""Small, conservative TeX lexer shared by the source check and link generator.

This is not a TeX interpreter. It handles the literal syntax documented in
tools/VALIDATION.md; it never expands macros or changes catcodes.
Offsets are retained, so a skipped region can never move a generated edit.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterator


class TexError(ValueError):
    """Malformed or unsupported source syntax."""


@dataclass(frozen=True)
class Command:
    name: str
    start: int
    end: int


COMMAND = re.compile(r'\\([A-Za-z@]+|[^\n])')
LITERAL_ENVS = {'verbatim', 'verbatim*', 'Verbatim', 'Verbatim*',
                'lstlisting', 'minted', 'comment'}
MATH_ENVS = {'math', 'displaymath', 'equation', 'equation*', 'align', 'align*',
             'alignat', 'alignat*', 'flalign', 'flalign*', 'gather', 'gather*',
             'multline', 'multline*', 'eqnarray', 'eqnarray*', 'split', 'aligned',
             'alignedat', 'gathered', 'array', 'cases', 'matrix', 'pmatrix',
             'bmatrix', 'Bmatrix', 'vmatrix', 'Vmatrix'}


def commands(text: str) -> Iterator[Command]:
    for match in COMMAND.finditer(text):
        yield Command(match[1], match.start(), match.end())


def skip_space(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def group(text: str, pos: int, opening: str = '{') -> tuple[str, int]:
    """Read a balanced mandatory/optional argument, respecting escaped braces."""
    pos = skip_space(text, pos)
    if pos >= len(text) or text[pos] != opening:
        raise TexError(f'expected {opening!r} argument near offset {pos}')
    closing = '}' if opening == '{' else ']'
    start = pos + 1
    stack = [closing]
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            match = COMMAND.match(text, pos)
            pos = match.end() if match else pos + 1
            continue
        ch = text[pos]
        if ch == '{':
            stack.append('}')
        elif ch == '[' and stack[-1] == ']':
            stack.append(']')
        elif ch == stack[-1]:
            stack.pop()
            if not stack:
                return text[start:pos], pos + 1
        pos += 1
    raise TexError(f'unclosed {opening!r} argument near offset {start - 1}')


def mask(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for pos in range(start, end):
            if chars[pos] != '\n':
                chars[pos] = ' '
    return ''.join(chars)


def literal_spans(text: str) -> list[tuple[int, int]]:
    """Comments, verbatim, and URL/detokenize arguments (not executable TeX)."""
    spans = []
    pos = 0
    while pos < len(text):
        if text[pos] == '%':
            end = text.find('\n', pos)
            end = len(text) if end < 0 else end
            spans.append((pos, end))
            pos = end
            continue
        if text[pos] != '\\':
            pos += 1
            continue
        match = COMMAND.match(text, pos)
        if match is None:
            pos += 1
            continue
        name, end = match[1], match.end()
        if name == 'verb':
            if end < len(text) and text[end] == '*':
                end += 1
            if end >= len(text) or text[end].isspace():
                raise TexError('missing delimiter after \\verb')
            close = text.find(text[end], end + 1)
            if close < 0 or '\n' in text[end:close]:
                raise TexError('unclosed \\verb')
            spans.append((pos, close + 1))
            end = close + 1
        elif name == 'begin':
            env, arg_end = group(text, end)
            if env in LITERAL_ENVS:
                closing = re.search(r'\\end\s*\{' + re.escape(env) + r'\}',
                                    text[arg_end:])
                if closing is None:
                    raise TexError(f'unclosed literal environment {env}')
                end = arg_end + closing.end()
                spans.append((pos, end))
        elif name in {'url', 'path', 'nolinkurl', 'detokenize', 'href'}:
            start = skip_space(text, end)
            if name == 'href' and start < len(text) and text[start] == '[':
                _, start = group(text, start, '[')
                start = skip_space(text, start)
            _, end = group(text, start)
            # Leave href's display argument available for reference checking.
            spans.append((start, end))
        pos = end
    return spans


def source_text(text: str) -> str:
    return mask(text, literal_spans(text))


def edition_text(text: str, results: bool, prefix: str = 'SCAFFOLD') -> str:
    """Evaluate supported conditionals, including multiple/nested glossary rows.

    Unknown conditionals fail closed rather than guessing glossary visibility.
    text is already stripped of comments and literal regions.
    """
    spans = []
    stack: list[tuple[bool, bool, bool]] = []  # parent, condition, seen_else
    active, pos = True, 0
    while pos < len(text):
        match = COMMAND.search(text, pos)
        end = match.start() if match else len(text)
        if not active:
            spans.append((pos, end))
        if match is None:
            break
        name, start, end = match[1], match.start(), match.end()
        if name in {'ifdefined', 'iftrue', 'iffalse'}:
            condition = name == 'iftrue'
            if name == 'ifdefined':
                arg = COMMAND.match(text, skip_space(text, end))
                if arg is None or arg[1] != prefix + 'ResultsView':
                    raise TexError('unsupported \\ifdefined; expected \\'
                                   + prefix + 'ResultsView')
                condition, end = results, arg.end()
            stack.append((active, condition, False))
            active = active and condition
            spans.append((start, end))
        elif name == 'else':
            if not stack or stack[-1][2]:
                raise TexError('unmatched or repeated \\else')
            parent, condition, _ = stack[-1]
            stack[-1] = (parent, condition, True)
            active = parent and not condition
            spans.append((start, end))
        elif name == 'fi':
            if not stack:
                raise TexError('unmatched \\fi')
            active = stack.pop()[0]
            spans.append((start, end))
        elif name.startswith('if') and name != 'iff':
            raise TexError(f'unsupported conditional \\{name}')
        elif not active:
            spans.append((start, end))
        pos = end
    if stack:
        raise TexError('unclosed conditional (missing \\fi)')
    return mask(text, spans)


def link_blockers(text: str) -> list[tuple[int, int]]:
    """Deny linking in math, literal regions, commands and their arguments.

    Unknown macro arguments are protected too. This intentionally misses some
    safe prose rather than ever rewriting a literal argument optimistically.
    """
    spans = literal_spans(text)
    clean = mask(text, spans)
    pos = 0
    math_end: str | None = None
    math_start = 0
    envs: list[tuple[str, int]] = []
    while pos < len(clean):
        if clean[pos] == '$':
            delim = '$$' if clean.startswith('$$', pos) else '$'
            if math_end is None:
                math_end, math_start = delim, pos
            elif math_end == delim:
                spans.append((math_start, pos + len(delim)))
                math_end = None
            pos += len(delim)
            continue
        match = COMMAND.match(clean, pos)
        if match is None:
            pos += 1
            continue
        name, end = match[1], match.end()
        if name in {'(', '['}:
            if math_end is not None:
                raise TexError('nested math delimiter')
            math_end = ')' if name == '(' else ']'
            math_start = pos
        elif name in {')', ']'}:
            if math_end != name:
                raise TexError('unmatched math delimiter')
            spans.append((math_start, end))
            math_end = None
        if name in {'begin', 'end'}:
            env, arg_end = group(clean, end)
            if env in MATH_ENVS:
                if name == 'begin':
                    envs.append((env, pos))
                else:
                    if not envs or envs[-1][0] != env:
                        raise TexError(f'unmatched math environment {env}')
                    _, start = envs.pop()
                    spans.append((start, arg_end))
        # Protect the command token itself and all balanced optional/mandatory
        # arguments; including nested formatting, URLs and existing links.
        arg_pos = end
        if arg_pos < len(clean) and clean[arg_pos] == '*':
            arg_pos += 1
        while True:
            arg_pos = skip_space(clean, arg_pos)
            if arg_pos >= len(clean) or clean[arg_pos] not in '{[':
                break
            _, arg_pos = group(clean, arg_pos, clean[arg_pos])
            end = arg_pos
        spans.append((pos, end))
        # Continue through arguments too, so an internal math delimiter is
        # checked and the later closing delimiter is not seen as unmatched.
        pos = match.end()
    if math_end is not None or envs:
        raise TexError('unclosed math delimiter or environment')
    return spans
