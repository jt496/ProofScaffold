"""Adversarial regression tests; fixtures contain no worked mathematics.

These tests survive make init: the placeholder prefix is rewritten with the
rest of the project. They do not require TeX, Lean, a network, or third-party
Python packages.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'python'))
from check_manuscript import check, PREFIX
from link_all import generate, mark
from tex_source import TexError, edition_text, source_text


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.write('tex/results/r.tex', r'\label{r}\dfn{widget}')
        self.write('tex/routes/t.tex', r'\label{t}\term{widget}\ref{r}')
        self.write('tex/archive/a.tex', r'\label{a}')
        self.write('tex/glossary.tex', r'\gkey{widget}{widget} & \ref{r}')
        for edition, owners in [('results', 'r'), ('routes', 't'), ('archive', 'rta')]:
            paths = {'r': 'results/r', 't': 'routes/t', 'a': 'archive/a'}
            self.write(f'tex/manifests/{edition}.tex', '\n'.join(
                '\\input{tex/' + paths[owner] + '}' for owner in owners))
        self.write('tools/local-terms.txt', '# local terms\n')
        self.write('tools/link-all-terms.txt', 'widget: widget, widgets\n')

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def append(self, name, text):
        path = self.root / name
        path.write_text(path.read_text(encoding='utf-8') + '\n' + text, encoding='utf-8')

    def fails(self, message):
        with self.assertRaisesRegex(TexError, message):
            check(self.root)


class ManuscriptTests(Fixture):
    def test_valid_fixture(self):
        self.assertIn('checks pass', check(self.root))

    def test_comments_do_not_create_labels_or_references(self):
        self.append('tex/results/r.tex', '% \\label{r} \\ref{missing}\n')
        check(self.root)

    def test_verbatim_does_not_create_references(self):
        self.append('tex/results/r.tex', r'\verb|\ref{missing}|')
        self.append('tex/results/r.tex', '\\begin{verbatim}\n\\label{r}\n\\end{verbatim}')
        check(self.root)

    def test_escaped_percent_is_not_a_comment(self):
        self.append('tex/results/r.tex', r'\% \ref{missing}')
        self.fails('unknown label')

    def test_percent_after_linebreak_is_a_comment(self):
        self.append('tex/results/r.tex', r'\\% \ref{missing}')
        check(self.root)

    def test_commented_input_is_missing(self):
        self.write('tex/manifests/archive.tex', '%\\input{tex/results/r}\n'
                   '\\input{tex/routes/t}\n\\input{tex/archive/a}')
        self.fails('expected 1')

    def test_missing_results_input(self):
        self.write('tex/manifests/results.tex', '')
        self.fails('expected 1')

    def test_missing_routes_input(self):
        self.write('tex/manifests/routes.tex', '')
        self.fails('expected 1')

    def test_wrong_results_ownership(self):
        self.append('tex/manifests/results.tex', r'\input{tex/routes/t}')
        self.fails('expected 0')

    def test_wrong_routes_ownership(self):
        self.append('tex/manifests/routes.tex', r'\input{tex/results/r}')
        self.fails('expected 0')

    def test_duplicate_input(self):
        self.append('tex/manifests/archive.tex', r'\input{tex/results/r}')
        self.fails('2 times')

    def test_explicit_tex_suffix(self):
        self.write('tex/manifests/results.tex', r'\input {tex/results/r.tex}')
        check(self.root)

    def test_missing_file(self):
        self.append('tex/manifests/archive.tex', r'\input{tex/results/absent}')
        self.fails('missing or non-content')

    def test_unsupported_manifest_macro(self):
        self.append('tex/manifests/archive.tex', r'\loadallmodules')
        self.fails('unsupported manifest')

    def test_unknown_label(self):
        self.append('tex/results/r.tex', r'\ref{absent}')
        self.fails('unknown label')

    def test_duplicate_label(self):
        self.append('tex/routes/t.tex', r'\label{r}')
        self.fails('duplicate label')

    def test_results_cannot_reference_routes(self):
        self.append('tex/results/r.tex', r'\ref{t}')
        self.fails('results-to-companion')

    def test_glossary_cannot_reference_routes_ungated(self):
        self.append('tex/glossary.tex', r'\gkeyx{route}{route} & \ref{t}')
        self.fails('results-to-companion')

    def add_hidden_rows(self):
        self.append('tex/glossary.tex', '\\ifdefined\\' + PREFIX + 'ResultsView\\else\n'
                    r'\gkeyx{one}{one} & \ref{t}' + '\n' +
                    r'\gkeyx{two}{two} & \ref{t}' + '\n\\fi')

    def test_second_gated_glossary_row(self):
        self.add_hidden_rows()
        self.append('tex/results/r.tex', r'\term{two}')
        self.fails('no visible glossary row')

    def test_nested_gate(self):
        self.append('tex/glossary.tex', '\\ifdefined\\' + PREFIX + 'ResultsView\\else\n'
                    '\\iftrue\\gkeyx{hidden}{hidden} & \\ref{t}\\fi\\fi')
        self.append('tex/results/r.tex', r'\term{hidden}')
        self.fails('no visible glossary row')

    def test_route_can_use_hidden_row(self):
        self.add_hidden_rows()
        self.append('tex/routes/t.tex', r'\term{two}')
        check(self.root)

    def test_glossary_unknown_conditional_fails_closed(self):
        self.append('tex/glossary.tex', r'\ifdefined\Unknown\else\fi')
        self.fails('unsupported')

    def test_unclosed_gate(self):
        self.append('tex/glossary.tex', '\\ifdefined\\' + PREFIX + 'ResultsView\\else')
        self.fails('unclosed conditional')

    def test_duplicate_else(self):
        self.append('tex/glossary.tex', r'\iftrue\else\else\fi')
        self.fails('repeated')

    def test_missing_definition(self):
        self.append('tex/glossary.tex', r'\gkey{missing}{missing}')
        self.fails('no \\\\dfn')

    def test_definition_of_glossary_only_row(self):
        self.append('tex/glossary.tex', r'\gkeyx{bad}{bad}')
        self.append('tex/routes/t.tex', r'\dfn{bad}')
        self.fails('defines it')

    def test_undocumented_emphasis(self):
        self.append('tex/results/r.tex', r'\emph{new {nested} term}')
        self.fails('emphasised term')

    def test_link_allowlist_typo(self):
        self.append('tools/link-all-terms.txt', 'absent: absent')
        self.fails('no glossary row')

    def test_dense_links_cannot_target_hidden_rows(self):
        self.add_hidden_rows()
        self.append('tex/results/r.tex', 'two')
        self.append('tools/link-all-terms.txt', 'two: two')
        self.fails('dense linking would target hidden')

    def test_frontmatter_dependency(self):
        self.write('tex/frontmatter/results.tex', r'\ref{t}')
        self.fails('results-to-companion')

    def test_literal_url_not_reference(self):
        self.append('tex/results/r.tex', r'\url{https://example.test/\ref{missing}}')
        check(self.root)

    def test_href_display_reference_is_checked(self):
        self.append('tex/results/r.tex', r'\href{https://example.test/}{\ref{missing}}')
        self.fails('unknown label')

    def test_false_branch_reference_ignored(self):
        self.append('tex/results/r.tex', r'\iffalse\ref{missing}\fi')
        check(self.root)


class LinkTests(Fixture):
    def test_prose_is_linked(self):
        result, count = mark('a widget here', {'widget': ['widget']})
        self.assertEqual(result, r'a \termx{widget}{widget} here')
        self.assertEqual(count, 1)

    def test_protected_syntax_is_unchanged(self):
        samples = [r'$widget$', r'$$widget$$', r'\(widget\)', r'\[widget\]',
                   r'\verb|widget|', r'\verb*+widget+', r'% widget',
                   r'\begin{align}widget\end{align}',
                   r'\begin{equation*}widget\end{equation*}',
                   r'\begin{verbatim}widget\end{verbatim}',
                   r'\url{https://example.test/widget}',
                   r'\href{https://example.test/widget}{widget}',
                   r'\unknown[widget]{outer {widget}}',
                   r'\section[widget]{nested \textbf{widget}}',
                   r'\termas{widget}{widget}', r'\label{widget}',
                   r'\widget', r'\detokenize{widget}']
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(mark(sample, {'widget': ['widget']}), (sample, 0))

    def test_linking_is_idempotent(self):
        result, _ = mark('widget', {'widget': ['widget']})
        self.assertEqual(mark(result, {'widget': ['widget']}), (result, 0))

    def test_match_must_not_cross_comment(self):
        text = 'first% ignored\n second'
        self.assertEqual(mark(text, {'term': ['first second']}), (text, 0))

    def test_whitespace_is_preserved(self):
        result, _ = mark('special\n  widget', {'term': ['special widget']})
        self.assertEqual(result, '\\termx{term}{special\n  widget}')

    def test_incomplete_math_fails_closed(self):
        with self.assertRaises(TexError):
            mark(r'\(widget', {'widget': ['widget']})

    def test_root_output_cannot_delete_source(self):
        before = (self.root / 'tex/results/r.tex').read_bytes()
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            generate(self.root, self.root)
        self.assertEqual((self.root / 'tex/results/r.tex').read_bytes(), before)

    def test_output_inside_source_refused(self):
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            generate(self.root / 'tex' / 'nested', self.root)

    def test_symlink_output_refused(self):
        out = self.root / 'alias'
        out.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            generate(out, self.root)
        self.assertTrue((self.root / 'tex/results/r.tex').exists())

    def test_custom_unmarked_tree_is_not_deleted(self):
        self.write('custom/tex/user-file', 'keep me')
        with self.assertRaisesRegex(ValueError, 'unmarked'):
            generate(self.root / 'custom', self.root)
        self.assertEqual((self.root / 'custom/tex/user-file').read_text(), 'keep me')

    def test_source_symlinks_refused(self):
        (self.root / 'tex/results/alias.tex').symlink_to(self.root / 'tex/results/r.tex')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            generate(self.root / 'build/linked-src', self.root)

    def test_generated_tree_can_be_replaced(self):
        out = self.root / 'custom'
        generate(out, self.root)
        generate(out, self.root)
        self.assertTrue((out / 'tex/.proof-linked-tree').is_file())

    def test_failed_generation_preserves_old_output(self):
        out = self.root / 'custom'
        generate(out, self.root)
        previous = (out / 'tex/results/r.tex').read_bytes()
        self.append('tex/results/r.tex', r'\(unclosed')
        with self.assertRaises(TexError):
            generate(out, self.root)
        self.assertEqual((out / 'tex/results/r.tex').read_bytes(), previous)
        self.assertFalse(list(out.glob('.link-stage-*')))

    def test_failed_publish_restores_old_output(self):
        import link_all
        out = self.root / 'custom'
        generate(out, self.root)
        previous = (out / 'tex/results/r.tex').read_bytes()
        real_replace = os.replace
        def fail_publish(source, destination):
            if Path(source).name == 'tex' and '.link-stage-' in str(source):
                raise OSError('simulated failed publish')
            return real_replace(source, destination)
        with patch.object(link_all.os, 'replace', side_effect=fail_publish):
            with self.assertRaises(OSError):
                generate(out, self.root)
        self.assertEqual((out / 'tex/results/r.tex').read_bytes(), previous)


@unittest.skipUnless(shutil.which('git') and shutil.which('make'), 'git and make required')
class PushTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'repo'
        self.root.mkdir()
        self.env = dict(os.environ)
        for key in list(self.env):
            if key.startswith('GIT_') or key in {'MAKEFLAGS', 'MFLAGS'}:
                self.env.pop(key)
        self.env.update(GIT_AUTHOR_NAME='Test', GIT_COMMITTER_NAME='Test',
                        GIT_AUTHOR_EMAIL='test@example.invalid',
                        GIT_COMMITTER_EMAIL='test@example.invalid',
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        self.git('init', '-q')
        self.git('config', 'core.hooksPath', '/dev/null')
        self.good = self.commit(True)
        self.bad = self.commit(False)
        self.hook = ROOT / '.githooks/pre-push'

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       env=self.env, text=True).strip()

    def commit(self, good):
        (self.root / 'Makefile').write_text('all:\n\t@' + ('true' if good else 'false') + '\n')
        self.git('add', 'Makefile')
        self.git('commit', '-qm', 'passing' if good else 'failing')
        return self.git('rev-parse', 'HEAD')

    def run_hook(self, *objects):
        data = ''.join(f'refs/heads/topic {oid} refs/heads/topic {"0" * 40}\n'
                       for oid in objects)
        return subprocess.run(['bash', str(self.hook)], cwd=self.root, env=self.env,
                              input=data, text=True, capture_output=True)

    def test_dirty_fix_cannot_hide_bad_commit(self):
        (self.root / 'Makefile').write_text('all:\n\t@true\n')
        result = self.run_hook(self.bad)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'Makefile').read_text(), 'all:\n\t@true\n')
        self.assertEqual(self.git('worktree', 'list', '--porcelain').count('worktree '), 1)

    def test_pushing_good_noncurrent_branch_passes(self):
        result = self.run_hook(self.good)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.bad)

    def test_every_pushed_tip_is_checked(self):
        self.assertNotEqual(self.run_hook(self.good, self.bad).returncode, 0)

    def test_build_cannot_consume_remaining_ref_records(self):
        (self.root / 'Makefile').write_text('all:\n\t@cat >/dev/null\n')
        self.git('add', 'Makefile')
        self.git('commit', '-qm', 'build reads stdin')
        reader = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(self.run_hook(reader, self.bad).returncode, 0)

    def test_duplicate_tips_built_once(self):
        result = self.run_hook(self.good, self.good)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('pre-push: make all at'), 1)

    def test_checkout_hooks_are_not_executed(self):
        hooks = self.root / 'hooks'
        hooks.mkdir()
        marker = self.root / 'checkout-ran'
        hook = hooks / 'post-checkout'
        hook.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n')
        hook.chmod(0o755)
        self.git('config', 'core.hooksPath', str(hooks))
        result = self.run_hook(self.good)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())

    def test_deletion_does_not_build(self):
        result = self.run_hook('0' * 40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('make all', result.stdout)

    def test_annotated_tag_is_peeled(self):
        self.git('tag', '-a', 'good', self.good, '-m', 'good')
        result = self.run_hook(self.git('rev-parse', 'good'))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_noncommit_tag_is_refused(self):
        result = self.run_hook(self.git('rev-parse', 'HEAD:Makefile'))
        self.assertNotEqual(result.returncode, 0)

    def test_exported_git_environment_is_cleared(self):
        self.env['GIT_DIR'] = str(self.root / '.git')
        self.env['GIT_WORK_TREE'] = str(self.root)
        result = self.run_hook(self.good)
        self.assertEqual(result.returncode, 0, result.stderr)


class LogTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_missing_log_fails(self):
        from check_latex_logs import check_logs
        with self.assertRaises(OSError):
            check_logs([self.root / 'absent.log'])

    def test_empty_log_list_fails(self):
        from check_latex_logs import check_logs
        with self.assertRaises(ValueError):
            check_logs([])

    def test_reference_warning_fails(self):
        from check_latex_logs import check_logs
        path = self.root / 'bad.log'
        path.write_text('LaTeX Warning: There were undefined references.\n')
        with self.assertRaises(ValueError):
            check_logs([path])

    def test_every_log_is_read(self):
        from check_latex_logs import check_logs
        path = self.root / 'good.log'
        path.write_text('Output written.\n')
        with self.assertRaises(OSError):
            check_logs([path, self.root / 'absent.log'])

    def test_complete_success_logs_pass(self):
        from check_latex_logs import check_logs
        paths = []
        for i in range(6):
            path = self.root / f'{i}.log'
            path.write_text('Output written.\n')
            paths.append(path)
        check_logs(paths)


class InitCompatibilityTests(Fixture):
    def test_checker_works_after_prefix_rewrite(self):
        new_prefix = 'INITIALIZED'
        directory = self.root / 'tools/python'
        directory.mkdir(parents=True)
        for path in (ROOT / 'tools/python').glob('*.py'):
            text = path.read_text(encoding='utf-8').replace(PREFIX, new_prefix)
            (directory / path.name).write_text(text, encoding='utf-8')
        self.append('tex/glossary.tex', '\\ifdefined\\' + new_prefix +
                    'ResultsView\\else\\gkeyx{hidden}{hidden} & \\ref{t}\\fi')
        command = [sys.executable, str(directory / 'check_manuscript.py')]
        good = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.append('tex/results/r.tex', r'\term{hidden}')
        bad = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('no visible glossary row', bad.stderr)

    def test_initializer_audit_replacement_contract_is_preserved(self):
        text = (ROOT / 'Makefile').read_text()
        pattern = r'(?m)^audit: tools\n(?:\t.*\n)+'
        replaced, count = re.subn(pattern, 'audit: tools\n\ttools/cpp/example 10\n', text)
        self.assertEqual(count, 1)
        self.assertIn('smoke: audit', replaced)
        self.assertIn('check-source:', replaced)
        self.assertIn('test:', replaced)

    def test_perl_compatibility_entrypoint(self):
        result = subprocess.run(['perl', str(ROOT / 'tools/check_manuscript.pl')],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class InitEndToEndTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / 'tools/init_project.py').is_file(),
                         'requires the complete repository initializer')
    def test_initialized_project_checks_and_links(self):
        # Keep the original template prefix out of the initializer's rewrite.
        if PREFIX != 'SCAF' + 'FOLD':
            self.skipTest('the one-time initializer is inactive after project naming')
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns(
                '.git', '.lake', 'build', 'output', '__pycache__', '*.pyc'))
            (project / 'output/standalone').mkdir(parents=True, exist_ok=True)
            commands = [
                [sys.executable, 'tools/init_project.py', '--name', 'Fixture',
                 '--title', 'Fixture project', '--authors', 'Test Author'],
                ['make', 'check-source'],
                [sys.executable, 'tools/python/link_all.py'],
            ]
            for command in commands:
                result = subprocess.run(command, cwd=project, text=True,
                                        capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run(['make', '-n', 'audit'], cwd=project,
                                    text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('tools/cpp/example 10', result.stdout)
            self.assertNotIn('tools/cpp/goldbach', result.stdout)
            self.assertFalse((project / 'tools/python/distinct_goldbach.py').exists())


if __name__ == '__main__':
    unittest.main()
