#!/usr/bin/python
#输出拼音字符
import argparse
import os
import pypinyin
from pypinyin import pinyin, Style, lazy_pinyin
import sys

#生成音调文件
def gen_label_txt(labeltxt)：
    result = lazy_pinyin(sys.argv[1], style=Style.TONE3, neutral_tone_with_five=True)
    print(' '.join(result))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件

    parser.add_argument(
        "--output",
        type=str,
        default="../../output/splits/lables.txt",
        help="directory split audio")

    args = parser.parse_args()

    gen_label_txt（output=args.output)

