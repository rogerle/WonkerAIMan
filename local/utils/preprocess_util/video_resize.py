
import argparse, os, cv2, traceback, subprocess
from glob import glob
from os import listdir, path

import ffmpeg
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument("--data_root", help="Root folder of the processed dataset", required=True)

args = parser.parse_args()


def main(args):
    print('Started clip man films for {} '.format(args.data_root, args.ngpu))

    filelist = glob(path.join(args.data_root, '*/*.mp4'))
    template_cpu_cut = 'ffmpeg -ss {} -i {} -hide_banner -c:v libx264 -t {} -y -r 25 {} >> exp/log/ffmpeg.log 2>&1'
    template_gpu_264__cut = 'ffmpeg -hwaccel cuda -c:v h264_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {} >> exp/log/ffmpeg.log 2>&1'
    template_gpu_265__cut = 'ffmpeg -hwaccel cuda -c:v hevc_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {} >> exp/log/ffmpeg.log 2>&1'
    path_idx=0

    for vfile in filelist:
        print('start processing file {}'.format(vfile))
        try:
            probe=ffmpeg.probe(vfile)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream is None:
                print('No video stream found!')
                return
            duration = float(video_stream['duration'])
            code_c = video_stream['codec_name']
            if args.ngpu == 0:
                template = template_cpu_cut
            elif code_c == 'h264':
                template = template_gpu_264__cut
            else:
                template = template_gpu_265__cut
            vfile_abs = os.path.abspath(vfile)
            name, ext = os.path.splitext(vfile_abs)
            new_duration = 180
            if duration > new_duration:
                time = range(0,int(duration),new_duration)
                for i in tqdm(time):
                    start_time = i
                    stop_time = i + new_duration
                    T1, T2 = [int(1000 * t) for t in [start_time, stop_time]]
                    filename = "%s_%d_%d%s" % (name,T1,T2,ext)
                    output_file = os.path.join(vfile_abs, filename)
                    cmd = template.format(start_time, vfile_abs, new_duration, output_file)
                    subprocess.call(cmd,shell=True)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()
            continue


if __name__ == '__main__':
    main(args)