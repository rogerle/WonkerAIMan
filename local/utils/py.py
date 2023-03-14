#!/usr/bin/python
import pypinyin
from pypinyin import pinyin, Style, lazy_pinyin
import sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        result = lazy_pinyin(sys.argv[1], style=Style.TONE3, neutral_tone_with_five=True)
        print(' '.join(result))

