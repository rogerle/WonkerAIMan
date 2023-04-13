import base64
import json
import requests
import numpy as np
import argparse, os, cv2, traceback, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from comm.base_comm import logger
from tqdm import tqdm
from glob import glob
from os import listdir, path
from decord import VideoReader, gpu, cpu
import ffmpeg

parser = argparse.ArgumentParser()

parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--face_server_ip', help='The face recogonition server', default='127.0.0.1')
parser.add_argument('--face_port', help='The face recogonition server', default='8866')
parser.add_argument('--face_detect', help='The face detector model', default='pyramidbox_lite_server')
parser.add_argument('--face_recognition', help='The face recognition model', default='resnet50_vd_imagenet_ssld')
parser.add_argument("--data_root", help="Root folder of the processed dataset", required=True)
parser.add_argument("--output", help="folder of the preprocessed dataset", required=True)

args = parser.parse_args()


def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')


def contain_man(img, detect_url, recog_url):
    is_man = False
    de_url = detect_url
    re_url = recog_url
    if img is None:
        return is_man
    # 判断这个图形是否有脸存在，如果有就返回脸的数据
    try:
        d_data = {'images': [cv2_to_base64(img)]}
        headers = {"Content-type": "application/json"}
        d_d = requests.post(url=de_url, headers=headers, data=json.dumps(d_data))
        if len(d_d.json()['results']) > 0:
            d_data = d_d.json()['results'][0]
            if d_data['data']:
                for face in d_data['data']:
                    locals().update(face)
                    if face['confidence'] < 0.8:
                        continue
                    else:
                        bottom, confidence, left, right, top = face.values()
                        crop = img[max(0,int(left - 10)):int(right + 10), max(0,int(top - 10)):int(bottom + 10), :]
                        if crop.size()<=0:continue
                        r_data = {'images': [cv2_to_base64(crop)], 'top_k': 2}
                        r_d = requests.post(url=re_url, headers=headers, data=json.dumps(r_data))
                        if r_d.json()['results']:
                            r_data = r_d.json()['results']['data']
                            for dic in r_data:
                                if dic and dic.get('0') > 0.9:
                                    is_man = True
                                    break
    except Exception as exc:
        logger.error('detect face err {}'.format(exc))
        is_man = False
    return is_man


def process_video_file(vfile, detect_url, recog_url, args, output_path):
    # 判断编码来确定用哪个转码
    ffmpeg_264_command = "ffmpeg -hwaccel cuda -c:v h264_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {} >> exp/log/ffmpeg.log 2>&1"
    ffmpeg_265_command = "ffmpeg -hwaccel cuda -c:v hevc_cuvid -ss {} -i {} -c:v h264_nvenc -t {} -y -r 25 {} >> exp/log/ffmpeg.log 2>&1"
    probe = ffmpeg.probe(vfile)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    code_c = video_stream['codec_name']
    if code_c == 'h264':
        ffmpeg_command = ffmpeg_264_command
    else:
        ffmpeg_command = ffmpeg_265_command

    print("start process the file {}".format(vfile))
    vr = VideoReader(vfile, ctx=gpu(0), width=512, height=512)
    av_fps = vr.get_avg_fps()
    frame_len = len(vr)
    try:
        frames = vr.get_batch(list(range(frame_len))[::1]).asnumpy()
    except Exception as exc:
        logger.error('decord stream err {}'.format(exc))
    vr.seek(0)
    # 定义片段的长度
    fragment_len = 5
    # 整个视频分割成片段
    split_arr = np.array_split(frames, int((frame_len / av_fps) / fragment_len))
    vfile_abs = os.path.abspath(vfile)
    basename = os.path.basename(vfile)
    name, ext = os.path.splitext(basename)

    for i, split_frames in enumerate(tqdm(split_arr, unit='frag')):
        if split_frames is not None:
            extra_flag = False
            for j, img in enumerate(split_frames):
                if i == 0 and j == 0:
                    continue
                if img is not None:
                    flag = contain_man(img, detect_url, recog_url)
                if not flag:
                    extra_flag = False
                    break
                else:
                    extra_flag = True
            # 只要有不属于这个up主的frame，这段5秒视频就丢弃,不然就保存
            if extra_flag:
                start_time = i * fragment_len
                T1, T2 = [int(1000 * t) for t in [start_time, start_time + fragment_len]]

                filename = "%sSUB%d_%d%s" % (name, T1, T2, ext)
                output_file = os.path.join(output_path, filename)

                cmd = ffmpeg_command.format(start_time, vfile_abs, fragment_len, output_file)
                subprocess.call(cmd, shell=True)


def main(args):
    print('Started clip man films for {} '.format(args.data_root, args.ngpu))

    filelist = glob(path.join(args.data_root, '*/*.mp4'))

    ##*如果有多个CPU可以把这里的多线程打开
    ##jobs = [(vfile, args, i % args.ngpu) for i, vfile in enumerate(filelist)]
    ##p = ThreadPoolExecutor(args.ngpu)
    ##futures = [p.submit(mp_handler, j) for j in jobs]
    ##_ = [r.result() for r in tqdm(as_completed(futures), total=len(futures))]

    detect_url = 'http://' + args.face_server_ip + ':' + args.face_port + '/predict/' + args.face_detect
    recog_url = 'http://' + args.face_server_ip + ':' + args.face_port + '/predict/' + args.face_recognition
    path_idx = 0
    for vfile in filelist:
        try:
            output_path = os.path.abspath(args.output)
            path_idx += 1
            new_out_path = Path(os.path.join(output_path, '{0:07d}'.format(path_idx)))
            new_out_path.mkdir(parents=True, exist_ok=True)
            process_video_file(vfile, detect_url, recog_url, args, new_out_path)
        except KeyboardInterrupt:
            exit(0)
        except:
            traceback.print_exc()
            continue


if __name__ == '__main__':
    main(args)
