import argparse
from pathlib import Path

import paddle
from paddlespeech.cli.tts import TTSExecutor
from paddlespeech.t2s.exps.syn_utils import get_sentences
tts_executor = TTSExecutor()

def gen_soundfie(args):

    sentences = get_sentences(text_file=args.sentences_txt, lang=args.lang)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    for utt_id, sentence in sentences:
        wav_file = tts_executor(
            text=sentence,
            output='{0}/{1}.wav'.format(output_dir,utt_id),
            am=args.am,
            am_config=args.am_config,
            am_ckpt=args.am_ckpt,
            am_stat=args.am_stat,
            spk_id=args.spk_id,
            phones_dict=args.phones_dict,
            tones_dict=None,
            speaker_dict=args.speaker_dict,
            voc=args.voc,
            voc_config=args.voc_config,
            voc_ckpt=args.voc_ckpt,
            voc_stat=args.voc_stat,
            lang=args.lang,
            device=paddle.get_device())
        print('Wave file has been generated: {}'.format(wav_file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")
    ##建立的人的声音文件

    parser.add_argument(
        "--output",
        type=str,
        default="exp/output",
        help="输出的地址")

    parser.add_argument(
        "--am",
        type=str,
        default="fastspeech2_csmsc",
        help="tts")

    parser.add_argument(
        "--am_config",
        type=str,
        default=None,
        help="tts")

    parser.add_argument(
        "--am_ckpt",
        type=str,
        default=None,
        help="tts")

    parser.add_argument(
        "--am_stat",
        type=str,
        default=None,
        help="tts")

    parser.add_argument(
        "--spk_id",
        type=int,
        default=0,
        help="tts")

    parser.add_argument(
        "--phones_dict",
        type=str,
        default=None,
        help="tts")

    parser.add_argument(
        "--speaker_dict",
        type=str,
        default=None,
        help="tts")

    parser.add_argument(
        "--tones_dict",
        type=str,
        default=None,
        help="tone dict")

    parser.add_argument(
        "--voc",
        type=str,
        default="pwgan_csmsc",
        help="音调训练模型")

    parser.add_argument(
        "--voc_config",
        type=str,
        default=None,
        help="音调配置文件")

    parser.add_argument(
        "--voc_ckpt",
        type=str,
        default=None,
        help="voc的checkpoint")

    parser.add_argument(
        "--voc_stat",
        type=str,
        default=None,
        help="voc的状态")

    parser.add_argument(
        "--lang",
        type=str,
        default="zh",
        help="directory split audio")

    parser.add_argument(
        "--ngpu",
        type=int,
        default=0,
        help="directory split audio")

    parser.add_argument(
        "--sentences_txt",
        type=str,
        default="data/source/sentences_mix.txt",
        help="directory split audio")

    args = parser.parse_args()

    if args.ngpu == 0:
        paddle.set_device("cpu")
    elif args.ngpu > 0:
        paddle.set_device("gpu")
    else:
        print("ngpu should >= 0 !")

    gen_soundfie(args)