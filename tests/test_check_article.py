import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/check_article.py'


class ArticleCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('check_article', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def inspect(self, text, stage='awaiting-title'):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'article.md'
            path.write_text(text, encoding='utf-8')
            before = path.read_bytes()
            findings = self.module.check_article(path, stage)
            self.assertEqual(path.read_bytes(), before)
            return findings

    def test_awaiting_title_accepts_body_without_h1(self):
        self.assertEqual(self.inspect('正文。\n\n内容来源，用户提供的文本。\n'), [])

    def test_ready_requires_first_nonempty_line_h1(self):
        result = self.inspect('正文。\n内容来源，用户提供的文本。', 'ready')
        self.assertIn('missing_title', [f['code'] for f in result])
        self.assertEqual(self.inspect('\n# 标题\n正文。\n内容来源，用户提供的文本。', 'ready'), [])

    def test_code_url_quotes_and_titles_are_protected(self):
        text = '''# 值得注意的是
```python
payload = {"items": [1, 2], "q": "值得注意的是?"}
# 内容来源，假来源不算正文注记。
```
~~~text
[图:00:30 - 留在引用代码中的标记]
~~~
    值得注意的是缩进代码。
> 值得注意的是，这是一条引文。
原话是“值得注意的是”。内联 `值得注意的是` 和 ``a ` 值得注意的是``。
[资源](https://example.com/watch?v=1&hint=值得注意的是)
https://example.com/值得注意的是?q=1
内容来源，用户提供文本。
'''
        self.assertEqual(self.inspect(text, 'ready'), [])

    def test_style_candidates_are_warnings_not_failures(self):
        findings = self.inspect('值得注意的是，这个条件成立。\n内容来源，用户提供文本。')
        self.assertTrue(findings)
        self.assertTrue(all(f['severity'] == 'warning' for f in findings))

    def test_technical_words_and_punctuation_are_allowed(self):
        text = '操作系统的差异具有统计显著性：结果如下。\n内容来源，用户提供文本。'
        self.assertEqual(self.inspect(text), [])

    def test_source_inside_code_does_not_satisfy_requirement(self):
        findings = self.inspect('正文。\n```text\n内容来源，伪注记。\n```')
        self.assertIn('missing_source', [f['code'] for f in findings])

    def test_placeholders_and_missing_images_fail_delivery(self):
        findings = self.inspect('正文。\n[图:00:30 - 某图]\n![图](missing.jpg)\n内容来源，文本。')
        self.assertEqual({f['code'] for f in findings}, {'placeholder', 'missing_image'})

    def test_draft_allows_unfinished_delivery(self):
        findings = self.inspect('[图:00:30 - 某图]', 'draft')
        self.assertTrue(all(f['severity'] != 'error' for f in findings))

    def test_real_image_and_remote_images_are_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'article.md'
            (Path(tmp) / 'figure one.jpg').write_bytes(b'image')
            path.write_text('![本地图](<figure one.jpg>)\n![远程图](https://example.com/a.jpg)\n内容来源，文本。')
            self.assertEqual(self.module.check_article(path, 'awaiting-title'), [])

    def test_unclosed_fence_is_an_error(self):
        findings = self.inspect('正文。\n```python\nx = 1\n内容来源，文本。')
        self.assertIn('unclosed_fence', [f['code'] for f in findings])

    def test_literal_html_comment_inside_code_does_not_hide_prose(self):
        text = '# 标题\n内容来源，文本。\n起始符是 `<!--`。\n[TODO:未完成]\n![图](missing.jpg)'
        findings = self.inspect(text, 'ready')
        self.assertEqual({f['code'] for f in findings}, {'placeholder', 'missing_image'})

    def test_indented_comment_literal_does_not_hide_source(self):
        self.assertEqual(self.inspect('    <!--\n\n内容来源，文本。'), [])

    def test_multiline_inline_code_is_protected(self):
        text = '代码示例 `\n[TODO:示例]\n![图](missing.jpg)\n`\n内容来源，文本。'
        self.assertEqual(self.inspect(text), [])

    def test_actual_html_comments_remain_protected(self):
        self.assertEqual(self.inspect('<!--\n![图](missing.jpg)\n[TODO:记录]\n-->\n内容来源，文本。'), [])

    def test_unpaired_backticks_do_not_hide_other_paragraphs(self):
        text = '# 标题\n原文包含未配对反引号 `。\n\n[TODO:未完成]\n![图](missing.jpg)\n\n另一个段落有反引号 `。\n内容来源，文本。'
        self.assertEqual({f['code'] for f in self.inspect(text, 'ready')}, {'placeholder', 'missing_image'})

    def test_fence_inside_html_comment_does_not_hide_following_prose(self):
        text = '# 标题\n<!--\n```python\n隐藏记录\n-->\n[TODO:未完成]\n![图](missing.jpg)\n内容来源，文本。'
        self.assertEqual({f['code'] for f in self.inspect(text, 'ready')}, {'placeholder', 'missing_image'})

    def test_comment_inside_fence_does_not_hide_following_prose(self):
        text = '# 标题\n```html\n<!--\n```\n[TODO:未完成]\n内容来源，文本。'
        self.assertEqual({f['code'] for f in self.inspect(text, 'ready')}, {'placeholder'})

    def test_balanced_and_escaped_image_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'article.md'
            (Path(tmp) / 'figure(1).jpg').write_bytes(b'image')
            path.write_text('![图](figure(1).jpg)\n![图](figure\\(1\\).jpg)\n![图](figure(1).jpg "caption")\n内容来源，文本。')
            self.assertEqual(self.module.check_article(path, 'awaiting-title'), [])

    def test_cli_reports_json_without_changing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'article.md'
            path.write_text('值得注意的是，正文。\n内容来源，文本。')
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--stage', 'awaiting-title', '--format', 'json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"warnings": 1', result.stdout)
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
