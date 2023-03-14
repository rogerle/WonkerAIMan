import argparse
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
from typing import Union

def split_wav(input_dir: Union[str,Path],
              output_dir: Union[str,Path]
              ):
    input_dir = Path(input_dir)
    print(input_dir)
    f_list = os.listdir(input_dir)
    for file in f_list:
        if os.path.splitext(file)[1] == '.wav':
            file = os.path.join(input_dir,file)
            print(file)
            aud = AudioSegment.from_wav(file)
            loudness = aud.dBFS
            chunks = split_on_silence(aud,
                                      min_silence_len=1000,
                                      silence_thresh=loudness - 6,
                                      keep_silence=True,
                                      seek_step=1
                                      )
            split_dir = Path(output_dir).expanduser()
            split_dir.mkdir(parents=True,exist_ok=True)

            #分割音频文件
            for i, chunk in enumerate(chunks):
                chunk.export("{0}/{1:05}.wav".format(split_dir, i + 1), format="wav")

            #输出分割的音频
            print("exported {0} chunks.".format(i + 1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件
    parser.add_argument(
        "--input_dir",
        type=str,
        default="../../data/source",
        help="directory containing audio")

    parser.add_argument(
        "--output_dir",
        type=str,
        default="../../output/splits",
        help="directory split audio")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    split_wav(
        input_dir=input_dir,
        output_dir=output_dir)