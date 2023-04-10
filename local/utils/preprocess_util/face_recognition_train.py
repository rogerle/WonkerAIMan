import argparse
import paddle
import paddlehub as hub
import paddlehub.vision.transforms as T
from paddlehub.finetune import Trainer

from wonkeraiman.datasets import FaceDataset


def parse_args():
    # parse args and config
    parser = argparse.ArgumentParser(
        description="finetue the imageclassification model")
    # 使用的基本模型
    parser.add_argument(
        '--data_root',
        type=str,
        default='"~/datasets/facedatas/wav2lips_face',
        help='使用训练的数据集，包括train_list.txt等文件的位置，默认在~/dataset/facedatas/wav2lips_face')

    parser.add_argument(
        '--pretrain_model',
        type=str,
        default='resnet50_vd_imagenet_ssld',
        help='使用的预训练模型是哪个，目前默认是resnet50_vd_imagenet_ssld')

    parser.add_argument(
        '--device', type=str, default='cpu', help='使用的训练设备，默认是cpu，使用gpu请输入gpu.')

    parser.add_argument(
        '--ckpt_dir',
        type=str,
        default='./img_classification_ckpt',
        help='输出的checkpoint的目录.')

    parser.add_argument(
        '--batch_size',
        type=int,
        default=8,
        help='训练时的batch_size，请根据自己显卡确定,默认8')

    parser.add_argument(
        '--epcho',
        type=int,
        default=100,
        help='训练循环次数')

    parser.add_argument(
        '--save_interval',
        type=int,
        default=10,
        help='保存checkpoint的周期')

    parser.add_argument(
        '--save_log_interval',
        type=int,
        default=10,
        help='保存训练Log的周期')

    args = parser.parse_args()
    return args


def train(dataset, val_dataset, args):
    ckpPath = args.ckpt_dir
    pre_model = args.pretrain_model
    epoch_time = args.epcho
    batch_size = args.batch_size
    save_interval = args.save_interval
    log_interval = args.save_log_interval

    if args.device == 'gpu':
        gpu = True
    else:
        gpu = False

    model = hub.Module(name=pre_model, label_list=["0", "1"])

    optimizer = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters())
    trainer = Trainer(model, optimizer, checkpoint_dir=ckpPath, use_gpu=gpu, use_vdl=True)

    trainer.train(dataset, epochs=epoch_time, batch_size=batch_size, eval_dataset=val_dataset,
                  save_interval=save_interval, log_interval=log_interval)


def pre_data_process(data_root, transforms, mode: str = 'train'):
    dataset = FaceDataset(transforms, mode=mode, dataset_dir=data_root)
    dataset_validate = FaceDataset(transforms, mode='val', dataset_dir=data_root)

    return dataset, dataset_validate


if __name__ == "__main__":
    args = parse_args()

    transforms = T.Compose([T.Resize((256, 256)),
                            T.CenterCrop(224),
                            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])],
                           to_rgb=True)
    data_root = args.data_root
    dataset, dataset_validate = pre_data_process(data_root, transforms, 'train')
    train(dataset, dataset_validate, args)
