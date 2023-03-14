from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

aud = AudioSegment.from_wav("input_data/hunter.wav")

loudness = aud.dBFS

chunks = split_on_silence(aud,
                          min_silence_len=1000,
                          silence_thresh=loudness-6,
                          keep_silence=True,
                          seek_step=1
                         )
split_dir = "splits"
if not os.path.exists(split_dir):
    os.mkdir(split_dir)
for i, chunk in enumerate(chunks):
    chunk.export("{0}/{1:05}.wav".format(split_dir, i+1), format="wav")

print("exported {0} chunks.".format(i+1))
