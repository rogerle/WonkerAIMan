import argparse
import soundfile as sf

from paddlespeech.server.engine.tts.paddleinference.tts_engine import TTSEngine


def changeSpeed(args):
    sig, samplerate = sf.read(args.wave_file)
    engine = TTSEngine()
    engine.postprocess(args.wave_file, samplerate, 16000,1,speed,args.output)

if __name__ == "main":
    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件
    parser.add_argument(
        "--wave_file",
        type=str,
        default=None,
        help="directory containing audio")

    parser.add_argument(
        "--speed",
        type=int,
        default=0,
        help="directory split audio")

    parser.add_argument(
        "--output",
        type=str,
        default="output/final",
        help="which wave file you want parse to train")
    args = parser.parse_args()
    changeSpeed(args)