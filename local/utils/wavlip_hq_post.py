import os
import random
import shutil
import cv2
from tqdm import tqdm
from os import path
import numpy as np
import threading

basePath = "."

# 需要的算法框架目录
wav2lipFolderName = 'Wav2Lip-master'
gfpganFolderName = 'GFPGAN-master'
wav2lipPath = basePath + '/' + wav2lipFolderName
gfpganPath = basePath + '/' + gfpganFolderName

# 确定需要制作的用户视频
userPath = "Mr数据杨"

# 获取本次需要合成视频的音频文件
userAudioPathList = os.listdir("inputs/" + userPath + "/source_audio")

for sourceAudioName in userAudioPathList:
    # 获取每个音频的名称
    title = sourceAudioName.split(".")[-2]
    # 每次随机从用户的原始文件中提取一个视频作为素材文件
    userVideoPathList = os.listdir("inputs/" + userPath + "/source_video")
    sourceVideoName = random.sample(userVideoPathList, 1)[0]

    # 输出项目目录
    outputPath = basePath + "/outputs/" + title
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    # 输入音频目录
    inputAudioPath = basePath + "/inputs/" + userPath + "/source_audio/" + sourceAudioName
    # 输入视频目录
    inputVideoPath = basePath + "/inputs/" + userPath + "/source_video/" + sourceVideoName
    # 视频数据输出目录
    lipSyncedOutputPath = basePath + '/outputs/' + title + "/result.mp4"

    # wav2lip生成cmd命令行处理数据
    cmd = "F:\MyEnvsProject\Wav2Lip\python.exe {}/inference.py --checkpoint_path {}/checkpoints/wav2lip_gan.pth --face {} --audio {} --outfile {} --resize_factor 2 --fps 60  --face_det_batch_size 8 --wav2lip_batch_size 128".format(
        wav2lipFolderName, wav2lipFolderName, inputVideoPath, inputAudioPath, lipSyncedOutputPath)
    os.system(cmd)

    # 将视频中的每一帧生成图片到目录中
    inputVideoPath = outputPath + '/result.mp4'
    unProcessedFramesFolderPath = outputPath + '/frames'

    if not os.path.exists(unProcessedFramesFolderPath):
        os.makedirs(unProcessedFramesFolderPath)

    # gpu_frame = cv2.cuda_GpuMat()

    vidcap = cv2.VideoCapture(inputVideoPath)
    numberOfFrames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    # print("FPS: ", fps, "Frames: ", numberOfFrames)

    for frameNumber in tqdm(range(numberOfFrames)):
        _, image = vidcap.read()
        cv2.imwrite(path.join(unProcessedFramesFolderPath, str(frameNumber).zfill(4) + '.jpg'), image)

    # 高清处理每一帧图片
    cmd = "F:\MyEnvsProject\Wav2Lip\python.exe {}/inference_gfpgan.py -i {} -o {} -v 1.3 -s 2 --only_center_face --bg_upsampler None".format(
        gfpganPath,
        unProcessedFramesFolderPath,
        outputPath)
    os.system(cmd)


    # def run_cmd(cmd):
    #     os.system(cmd)
    #
    #
    # for i in range(100):
    #     t = threading.Thread(target=run_cmd, args=(cmd,))
    #     t.start()

    # 根据视频创建每一帧的画面

    restoredFramesPath = outputPath + '/restored_imgs/'
    if not os.path.exists(restoredFramesPath):
        os.makedirs(restoredFramesPath)
    processedVideoOutputPath = outputPath

    dir_list = os.listdir(restoredFramesPath)
    dir_list.sort()

    batch = 0
    batchSize = 600

    for i in tqdm(range(0, len(dir_list), batchSize)):
        img_array = []
        start, end = i, i + batchSize
        print("processing ", start, end)
        for filename in tqdm(dir_list[start:end]):
            filename = restoredFramesPath + filename;
            img = cv2.imread(filename)
            if img is None:
                continue
            height, width, layers = img.shape
            size = (width, height)
            img_array.append(img)

        out = cv2.VideoWriter(processedVideoOutputPath + '/batch_' + str(batch).zfill(4) + '.mp4',
                              cv2.VideoWriter_fourcc(*'DIVX'), 60, size)
        batch = batch + 1

        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()

    # 最终合成视频
    concatTextFilePath = outputPath + "/concat.txt"
    concatTextFile = open(concatTextFilePath, "w", encoding='utf8')
    for ips in range(batch):
        concatTextFile.write("file batch_" + str(ips).zfill(4) + ".mp4\n")
    concatTextFile.close()

    concatedVideoOutputPath = outputPath + "/concated_output.mp4"
    cmd = "ffmpeg -y -f concat -i {} -c copy {}".format(concatTextFilePath, concatedVideoOutputPath)
    os.system(cmd)

    finalProcessedOutputVideo = processedVideoOutputPath + '/final_with_audio.mp4'
    cmd = "ffmpeg -y -i {} -i {} -map 0 -map 1:a -c:v copy -shortest {}".format(concatedVideoOutputPath, inputAudioPath,
                                                                                finalProcessedOutputVideo)
    os.system(cmd)
