import sys

import face_recognition
import numpy as np
import argparse, os, cv2, traceback, subprocess

from moviepy.editor import VideoFileClip
from tqdm import tqdm
from glob import glob
import face_detection
from os import listdir, path

if sys.version_info[0] < 3 and sys.version_info[1] < 2:
    raise Exception("Must be using >= Python 3.2")

parser = argparse.ArgumentParser()

parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--face', help='The face picture in video', required=True)
parser.add_argument("--data_root", help="Root folder of the processed dataset", required=True)
parser.add_argument("--output", help="folder of the preprocessed dataset", required=True)

args = parser.parse_args()

if not path.isfile('data/sfd/s3fd.pth'):
    raise FileNotFoundError('Save the s3fd model to face_detection/detection/sfd/s3fd.pth before running this script!')

fa = [face_detection.FaceAlignment(face_detection.LandmarksType._2D, flip_input=False,
                                   device='cuda:{}'.format(id)) for id in range(args.ngpu)]


def contain_man(img, man_encoding):
    unkonw_img = img.copy()
    face_locations = face_recognition.face_locations(unkonw_img)
    face_encodings = face_recognition.face_encodings(unkonw_img, face_locations)
    is_man = False
    for face_endcode in face_encodings:
        if face_endcode[0]:
            result = face_recognition.compare_faces([man_encoding], face_endcode[0])
            is_man = result[0]
    return is_man


def process_video_file(vfile, args, gpu_id=0):
    origin_image = face_recognition.load_image_file(args.face)
    o_face_encoding = face_recognition.face_encodings(origin_image)[0]

    clip = VideoFileClip(vfile)
    vfile_abs = os.path.abspath(vfile)
    name, ext = os.path.splitext(vfile_abs)
    start_time = 0
    stop_time = 0
    fps = 25
    duration_list = []

    # 对每帧视频进行处理，如果符合则保留时间
    for i, img in enumerate(tqdm(clip.iter_frames(fps=25))):
        flag = contain_man(img, o_face_encoding)
        if flag and start_time == 0:
            start_time = i / 25
            last_index = i
        if start_time > 0 and not flag:
            stop_time = i / 25
            duration_list.append([start_time, stop_time])
            start_time = stop_time = 0

    for i, d in tqdm(enumerate(duration_list)):
        start_d, end_d = d
        T1, T2 = [int(1000 * t) for t in [start_d, end_d]]
        filename = "%sSUB%d_%d%s" % (name, T1, T2, ext)
        time_len = round(end_d - start_d, 2)

        ffmpeg_command = "ffmpeg -hwaccel cuda -c:v h264_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {}"
        cmd = ffmpeg_command.format(start_d, vfile_abs, time_len, filename)
        subprocess.call(cmd, shell=True)


def main(args):
    print('Started clip man films for {} '.format(args.data_root, args.ngpu))

    filelist = glob(path.join(args.data_root, '*/*.mp4'))

    ##*如果有多个CPU可以把这里的多线程打开
    ##jobs = [(vfile, args, i % args.ngpu) for i, vfile in enumerate(filelist)]
    ##p = ThreadPoolExecutor(args.ngpu)
    ##futures = [p.submit(mp_handler, j) for j in jobs]
    ##_ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

    for vfile in filelist:
        try:
            process_video_file(vfile, args)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()
            continue


if __name__ == '__main__':
    main(args)
