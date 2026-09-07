#!/usr/bin/env python3
"""Check every expected build log; a missing or unreadable log is a failure."""
from pathlib import Path
import re
import sys

BAD_REFERENCE = re.compile(r'undefined references|multiply defined|There were undefined')


def check_logs(paths):
    if not paths:
        raise ValueError('no expected LaTeX logs supplied')
    for name in paths:
        path = Path(name)
        # TeX logs need not be valid UTF-8, but ASCII warning text is preserved.
        for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
            if BAD_REFERENCE.search(line):
                raise ValueError(f'{path}:{number}: {line}')


def main():
    try:
        check_logs(sys.argv[1:])
    except (OSError, ValueError) as error:
        print(f'LaTeX reference check failed: {error}', file=sys.stderr)
        return 1
    print('LaTeX reference check passes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
