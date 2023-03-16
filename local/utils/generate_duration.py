# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
from pathlib import Path
from local.utils.gen_duration_from_textgrid import gen_duration_from_textgrid

if __name__ == '__main__':
    # parse config and args
    parser = argparse.ArgumentParser(
        description="Preprocess audio and then extract features.")

    parser.add_argument(
        "--mfa_dir",
        type=str,
        default="./output/mfa_result",
        help="directory to save aligned files")

    parser.add_argument(
        "--durations_file",
        type=str,
        default="./output/durations.txt",
        help="directory to save aligned files")

    args = parser.parse_args()

    fs = 24000
    n_shift = 300
    durations_file = Path(args.durations_file)
    mfa_dir = Path(args.mfa_dir)
    mfa_dir.mkdir(parents=True, exist_ok=True)

    gen_duration_from_textgrid(mfa_dir, durations_file, fs, n_shift)
