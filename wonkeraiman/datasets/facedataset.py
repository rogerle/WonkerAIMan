import os
from typing import Callable, Tuple

import paddle
import numpy as np

# 自定义脸部的数据集
class FaceDataset(paddle.io.Dataset):
    def __init__(self, transforms: Callable, mode: str = 'train', dataset_dir: str = '~/datasets/facedatas/wav2lips_face'):
        # 数据集存放位置
        self.mode = mode
        self.transforms = transforms
        self.dataset_dir = dataset_dir

        if self.mode == 'train':
            self.file = 'train_list.txt'
        elif self.mode == 'test':
            self.file = 'test_list.txt'
        else:
            self.file = 'validate_list.txt'

        self.file = os.path.join(self.dataset_dir, 'wav2lips_face', self.file)

        with open(self.file, 'r') as file:
            self.data = file.read().split('\n')

    def __getitem__(self, idx) -> Tuple[np.ndarray, int]:
        img_path, grt = self.data[idx].split(' ')
        img_path = os.path.join(self.dataset_dir, 'wav2lips_face', img_path)
        im = self.transforms(img_path)
        return im, int(grt)

    def __len__(self):
        return len(self.data)
