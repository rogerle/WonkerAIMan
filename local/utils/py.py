#!/usr/bin/python
#输出拼音字符
import argparse
import os
import pypinyin
from pypinyin import pinyin, Style, lazy_pinyin
from pathlib import Path
from typing import Union
import sys

#生成音调文件
def gen_label_txt(content_txt:Union[str,Path],
                  labels_txt:Union[str,Path]
                  ):
        temp_py_word = []
        with open(content_txt, "r", encoding='utf-8') as f:
            for line in f.readline():
                result = lazy_pinyin(line, style=Style.TONE3, neutral_tone_with_five=True)
                print("the pinyin is {}".format(result))
                temp_py_word.append(result)
        f.close()

        with open(labels_txt, "w", encoding='utf-8') as fw:
            for line in temp_py_word:
                print(line)
                fw.write(line + "\n")
        fw.close()
        print('labels created')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件

    parser.add_argument(
        "--content_txt",
        type=str,
        default="../../output/lables.txt",
        help="directory split audio")

    parser.add_argument(
        "--labels_txt",
        type=str,
        default="../../output/lables.txt",
        help="directory split audio")
    args = parser.parse_args()

    content_txt = Path(args.content_txt)
    labels_txt = Path(args.labels_txt)
    gen_label_txt(content_txt,labels_txt)


