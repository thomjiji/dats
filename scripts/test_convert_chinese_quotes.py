#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from convert_chinese_quotes import convert_markdown


OPEN_DOUBLE = chr(0x201C)
CLOSE_DOUBLE = chr(0x201D)
OPEN_SINGLE = chr(0x2018)
CLOSE_SINGLE = chr(0x2019)


class ConvertChineseQuotesTests(unittest.TestCase):
    def test_converts_paired_quotes_in_chinese_prose(self):
        source = '他说 "hello"，还说 \'world\'。'
        expected = (
            "他说 "
            + OPEN_DOUBLE
            + "hello"
            + CLOSE_DOUBLE
            + "，还说 "
            + OPEN_SINGLE
            + "world"
            + CLOSE_SINGLE
            + "。"
        )
        self.assertEqual(expected, convert_markdown(source))

    def test_leaves_english_only_text_unchanged(self):
        source = 'He said "hello" and \'world\'.'
        self.assertEqual(source, convert_markdown(source))

    def test_skips_markdown_code_regions(self):
        source = (
            '正文 "保留"。\n\n'
            '```python\n'
            'print("中文")\n'
            '```\n\n'
            '`他说 "代码"`\n\n'
            '    他说 "代码"\n'
        )
        expected = (
            "正文 "
            + OPEN_DOUBLE
            + "保留"
            + CLOSE_DOUBLE
            + "。\n\n"
            "```python\n"
            "print(\"中文\")\n"
            "```\n\n"
            '`他说 "代码"`\n\n'
            '    他说 "代码"\n'
        )
        self.assertEqual(expected, convert_markdown(source))

    def test_leaves_apostrophes_and_unmatched_quotes(self):
        source = '他说 "It\'s ok"，以及 "未结束'
        expected = (
            "他说 "
            + OPEN_DOUBLE
            + "It's ok"
            + CLOSE_DOUBLE
            + "，以及 \"未结束"
        )
        self.assertEqual(expected, convert_markdown(source))

    def test_converts_nested_single_quotes(self):
        source = '他说 "外层 \'内层\'"。'
        expected = (
            "他说 "
            + OPEN_DOUBLE
            + "外层 "
            + OPEN_SINGLE
            + "内层"
            + CLOSE_SINGLE
            + CLOSE_DOUBLE
            + "。"
        )
        self.assertEqual(expected, convert_markdown(source))

    def test_leaves_unclosed_inline_code_unchanged(self):
        source = '正文 "正常"，`代码 "不转换"'
        expected = '正文 ' + OPEN_DOUBLE + '正常' + CLOSE_DOUBLE + '，`代码 "不转换"'
        self.assertEqual(expected, convert_markdown(source))


if __name__ == "__main__":
    unittest.main()
