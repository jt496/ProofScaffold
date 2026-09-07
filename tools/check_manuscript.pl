#!/usr/bin/env perl
# Compatibility entry point. The scanner is shared with the dense-link tool.
# Run from the repository root; see tools/VALIDATION.md for its precise scope.
use strict;
use warnings;
use FindBin;
exec($ENV{PYTHON} // 'python3', "$FindBin::Bin/python/check_manuscript.py", @ARGV)
    or die "cannot run manuscript checker: $!\n";
