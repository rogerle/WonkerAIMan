import argparse
import logging
import os
import pypinyin
import paddle
import librosa
import soundfile as sf
from paddlespeech.server.bin.paddlespeech_client import ASROnlineClientExecutor
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
from typing import Union
import logging

logging.getLogger("PaddleSpeech").setLevel(logging.WARNING)
def split_wav(wave_file: Union[str,Path],
              output_dir: Union[str,Path]
              ):
    wave_file = Path(wave_file)
    output_dir = Path(output_dir)
    print("start parse audio {}".format(wave_file))
    if os.path.splitext(wave_file)[1] == '.wav':
        print('start split wave files{}'.format(wave_file))
        aud = AudioSegment.from_wav(wave_file)
        loudness = aud.dBFS
        chunks = split_on_silence(aud,
                                  min_silence_len=1500,
                                  silence_thresh=loudness - 6,
                                  keep_silence=True,
                                  seek_step=1
                                  )
        file = os.path.split(wave_file)[1]
        split_name = os.path.splitext(file)[0]
        split_dir = Path(output_dir).joinpath(str(split_name))
        print('Split wave file to {}'.format(split_dir))
        split_dir.mkdir(parents=True, exist_ok=True)

        # 分割音频文件
        temp_cont_word = []
        sig, samplerate = sf.read(wave_file)
        for i, chunk in enumerate(chunks):
            split_wave_name = "{0}/{1:05}.wav".format(split_dir, i + 1)
            chunk.export(split_wave_name, format="wav")
            if samplerate != 16000:
                audio_src,sr = librosa.load(split_wave_name,samplerate)
                audio_16_K = librosa.resample(audio_src, orig_sr=sr, target_sr=16000)
                sf.write(split_wave_name, audio_16_K, 16000)
            print("chunk file {0}".format(split_wave_name))
            temp_cont_word.append(asr_wav(split_wave_name))
        print("exported {0} chunks.".format(i + 1))
        # 分割的音频转文字
        content_txt = Path(split_dir).joinpath("content.txt")

        with open(content_txt, "w", encoding='utf-8') as f:
            for line in temp_cont_word:
                f.write(line + "\n")
        f.close()




#语音识别出结果
def asr_wav(wavefile):
    asrclient_executor = ASROnlineClientExecutor()
    res = asrclient_executor(
        input=wavefile,
        server_ip="127.0.0.1",
        port=8190,
        sample_rate=16000,
        lang="zh_cn",
        audio_format="wav")
    return res

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

    parser.add_argument(
        "--audio_name",
        type=str,
        default="audio.wav",
        help="which wave file you want parse to train")
    args = parser.parse_args()

    wave_file = Path(args.input_dir + '/'+args.audio_name)
    output_dir = Path(args.output_dir)
    split_wav(
        wave_file=wave_file,
        output_dir=output_dir)
