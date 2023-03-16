#!/usr/bin/python
# 输出拼音字符
import argparse
from pypinyin import Style, lazy_pinyin
from pathlib import Path
from typing import Union
import sys


# 生成音调文件
def gen_label_txt(content_txt: Union[str, Path],
                  labels_txt: Union[str, Path]
                  ):
    temp_py_word = []
    with open(content_txt, "r", encoding='utf-8') as f:
        for line in f.readlines():
            result = lazy_pinyin(line, style=Style.TONE3, neutral_tone_with_five=True)
            temp_py_word.append(' '.join(result))
    f.close()

    with open(labels_txt, "w", encoding='utf-8') as fw:
        i = 0
        for line in temp_py_word:
            i = i + 1
            head = '{0:05}'.format(i) + '|'
            fw.write(head + line)
    fw.close()
    print('labels created')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件

    parser.add_argument(
        "--content_txt",
        type=str,
        default="../../output/content.txt",
        help="directory split audio")

    parser.add_argument(
        "--labels_txt",
        type=str,
        default="../../output/labels.txt",
        help="directory split audio")
    args = parser.parse_args()

    content_txt = Path(args.content_txt)
    labels_txt = Path(args.labels_txt)
    gen_label_txt(content_txt, labels_txt)
