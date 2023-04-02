import sys
import numpy as np
import argparse, os, cv2, traceback, subprocess
from tqdm import tqdm
from glob import glob
import face_detection
from os import listdir, path


if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

parser = argparse.ArgumentParser()

parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--batch_size', help='Single GPU Face detection batch size', default=12, type=int)
parser.add_argument("--data_root", help="Root folder of the processed dataset", required=True)
parser.add_argument("--output", help="folder of the preprocessed dataset", required=True)

args = parser.parse_args()

if not path.isfile('data/sfd/s3fd.pth'):
    raise FileNotFoundError('Save the s3fd model to face_detection/detection/sfd/s3fd.pth before running this script!')

fa = [face_detection.FaceAlignment(face_detection.LandmarksType._2D, flip_input=False,
                                   device='cuda:{}'.format(id)) for id in range(args.ngpu)]


def process_video_file(vfile, args, gpu_id=0):
    video_stream = cv2.VideoCapture(vfile)
    vfile_abs = os.path.abspath(vfile)
    name, ext = os.path.splitext(vfile_abs)
    frames = []
    while 1:
        still_reading, frame = video_stream.read()
        if not still_reading:
            video_stream.release()
            break
        frames.append(frame)
    start_time = 0
    stop_time =0
    fps = 25
    duration_list = []
    for j, frame in enumerate(tqdm(frames)):
        face = fa[0].get_detections_for_img(frame)
        if face is not None and start_time == 0:
            # 按每秒25帧计算
            start_time = j / fps

        if start_time > 0 and face is None:
            stop_time = j / fps
            duration_list.append([start_time,stop_time])

            start_time = stop_time = 0


    for i, d in tqdm(enumerate(duration_list)):
        start_d,end_d = d
        T1, T2 = [int(1000 * t) for t in [start_d, end_d]]
        filename = "%sSUB%d_%d%s" % (name, T1, T2, ext)
        time_len=round(end_d-start_d,2)

        ffmpeg_command = "ffmpeg -hwaccel cuda -c:v h264_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {}"
        cmd= ffmpeg_command.format(start_d, vfile_abs, time_len, filename)
        subprocess.call(cmd, shell=True)

def main(args):
    print('Started clip man films for {} '.format(args.data_root, args.ngpu))

    filelist = glob(path.join(args.data_root, '*/*.mp4'))

    ##*如果有多个CPU可以把这里的多线程打开
    ##jobs = [(vfile, args, i % args.ngpu) for i, vfile in enumerate(filelist)]
    ##p = ThreadPoolExecutor(args.ngpu)
    ##futures = [p.submit(mp_handler, j) for j in jobs]
    ##_ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

    for vfile in tqdm(filelist):
        try:
            process_video_file(vfile, args)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()
            continue


if __name__ == '__main__':
    main(args)
