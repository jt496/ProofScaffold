#!/usr/bin/env perl
# ---------------------------------------------------------------------------
# Consistency checks over the LaTeX sources.  Run by `make check`.
#
# What it enforces:
#   * no duplicate \label anywhere in the content modules;
#   * every \ref/\eqref names a label that exists;
#   * no results module refers to a route- or archive-owned label (the results
#     edition would not build, and the dependency must stay acyclic);
#   * the full manifest includes every content module exactly once, and names
#     no file that is missing;
#   * every \gkey glossary row is matched by exactly one \dfn, every \gkeyx row
#     by none, and every \term lands on some row;
#   * a glossary row gated out of the results edition is never \term-linked
#     from a results module (\hyperlink to a missing target fails silently, so
#     nothing else would catch it);
#   * every \emph in a content module is either a \dfn or acknowledged in
#     tools/local-terms.txt;
#   * every key in tools/link-all-terms.txt has a glossary row.
#
# The last of the \emph checks is what keeps the glossary honest as the project
# grows: a newly emphasised term fails the build until it is either given a row
# or recorded as local.
# ---------------------------------------------------------------------------
use strict;
use warnings;

# Basenames that must never reappear at the repository root -- typically a
# monolithic manuscript that was split up, and that a tool or an agent might
# regenerate.  Add patterns here after retiring an entry point.
my @RETIRED = ();

my $PREFIX  = 'SCAFFOLD';                 # LaTeX macro prefix, e.g. \SCAFFOLDResultsView
my $GLOSS   = 'tex/glossary.tex';
my $FULL_MANIFEST = 'tex/manifests/archive.tex';
my $LOCAL   = 'tools/local-terms.txt';
my $LINKALL = 'tools/link-all-terms.txt';

if (@RETIRED) {
    opendir my $root, '.' or die "cannot read project root: $!\n";
    my @found = sort grep { my $f = $_; grep { $f =~ /$_/ } @RETIRED } readdir $root;
    closedir $root;
    die "retired manuscript file(s) present: @found\n" if @found;
}

my @content = (glob('tex/results/*.tex'), glob('tex/routes/*.tex'),
               glob('tex/archive/*.tex'));
die "no content modules found; run from the repository root\n" unless @content;

sub slurp {
    my ($file) = @_;
    open my $fh, '<', $file or die "cannot read $file: $!\n";
    local $/;
    my $text = <$fh>;
    close $fh;
    return $text;
}

sub uncomment {
    my ($text) = @_;
    $text =~ s/(?<!\\)%.*//mg;
    return $text;
}

# --- labels: uniqueness, existence, and acyclic ownership ------------------
my (%owner, %refs);
for my $file (@content) {
    my $text = slurp($file);
    while ($text =~ /\\label\{([^}]+)\}/g) {
        die "duplicate label $1 in $owner{$1} and $file\n" if exists $owner{$1};
        $owner{$1} = $file;
    }
    while ($text =~ /\\(?:ref|eqref)\{([^}]+)\}/g) {
        $refs{$file}{$1} = 1;
    }
}
for my $file (@content) {
    for my $label (keys %{ $refs{$file} // {} }) {
        die "unknown label $label referenced by $file\n" unless exists $owner{$label};
        if ($file =~ m{^tex/results/} && $owner{$label} =~ m{^tex/(?:routes|archive)/}) {
            die "results-to-companion dependency: $file -> $label "
              . "($owner{$label}).  Either promote the statement into "
              . "tex/results/, or stop referring to it from the results "
              . "edition.\n";
        }
    }
}

# --- the full manifest must cover every module exactly once ----------------
my $manifest = slurp($FULL_MANIFEST);
my %input_count;
while ($manifest =~ /\\input\{(tex\/(?:results|routes|archive)\/[^}]+)\}/g) {
    ++$input_count{"$1.tex"};
}
for my $file (@content) {
    my $count = $input_count{$file} // 0;
    die "$FULL_MANIFEST includes $file $count times (expected once)\n"
        unless $count == 1;
}
for my $file (keys %input_count) {
    die "$FULL_MANIFEST names missing file $file\n" unless -f $file;
}

# --- the glossary is the single source of truth for terminology ------------
my $glosstext = uncomment(slurp($GLOSS));
my (%row, %gated);
while ($glosstext =~ /(\\ifdefined\\${PREFIX}ResultsView\\else\s*\n)?\\(gkeyx?)\{([^}]+)\}/g) {
    my ($gate, $kind, $key) = ($1, $2, $3);
    die "duplicate glossary row $key\n" if exists $row{$key};
    $row{$key}   = $kind;
    $gated{$key} = 1 if defined $gate;
}

my (%dfn, %termuse);
for my $file (@content) {
    my $text = uncomment(slurp($file));
    while ($text =~ /\\dfn(?:as)?\{([^}]+)\}/g) {
        die "term $1 defined twice: $dfn{$1} and $file\n" if exists $dfn{$1};
        $dfn{$1} = $file;
    }
    while ($text =~ /\\term(?:as)?\{([^}]+)\}/g) {
        $termuse{$1}{$file} = 1;
    }
}

for my $key (sort keys %row) {
    if ($row{$key} eq 'gkey') {
        die "glossary row $key has no \\dfn in the body; either add one or "
          . "mark the row \\gkeyx\n" unless exists $dfn{$key};
    } elsif (exists $dfn{$key}) {
        die "glossary row $key is marked \\gkeyx but $dfn{$key} defines it; "
          . "use \\gkey instead\n";
    }
}
for my $key (sort keys %dfn) {
    die "\\dfn{$key} in $dfn{$key} has no glossary row\n" unless exists $row{$key};
}
for my $key (sort keys %termuse) {
    die "\\term{$key} in " . join(', ', sort keys %{ $termuse{$key} })
      . " has no glossary row\n" unless exists $row{$key};
}

# --- emphasis coverage -----------------------------------------------------
my %allowed;
for my $line (split /\n/, slurp($LOCAL)) {
    next if $line =~ /\A\s*(?:#.*)?\z/;
    $line =~ s/\A\s+|\s+\z//g;
    $allowed{$line} = 1;
}
my @undocumented;
for my $file (@content) {
    my $text = uncomment(slurp($file));
    while ($text =~ /\\emph\{((?:[^{}]|\{[^{}]*\})*)\}/g) {
        my $term = $1;
        next if $term =~ /\\(?:ref|eqref|dfn|term)/;   # cross-references, markup
        next if $term =~ /\A[A-Z].*\.\z/s;             # run-in paragraph header
        $term =~ s/\s+/ /g;
        $term =~ s/\A\s+|\s+\z//g;
        push @undocumented, "$file: $term" unless $allowed{$term};
    }
}
die "emphasised terms that are neither a \\dfn nor listed in $LOCAL:\n"
  . join('', map { "  $_\n" } @undocumented) if @undocumented;

# --- gated rows must not be linked from the results edition ----------------
for my $key (sort keys %gated) {
    my @bad = grep { m{^tex/results/} } sort keys %{ $termuse{$key} // {} };
    die "\\term{$key} appears in " . join(', ', @bad)
      . ", but its glossary row is gated out of the results edition; either "
      . "ungate the row (pointing it at a results-owned label) or drop the "
      . "link\n" if @bad;
}

# --- all-occurrence linking must not point at nothing ----------------------
for my $line (split /\n/, slurp($LINKALL)) {
    next if $line =~ /\A\s*(?:#.*)?\z/;
    next unless $line =~ /\A\s*([^:]+?)\s*:/;
    die "$LINKALL lists '$1', which has no glossary row\n" unless exists $row{$1};
}

my $links = 0;
$links += scalar keys %{ $termuse{$_} } for keys %termuse;

printf "%d content modules; %d unique labels; %d glossary rows; %d term links; "
     . "all source, ownership and glossary checks pass\n",
     scalar(@content), scalar(keys %owner), scalar(keys %row), $links;
