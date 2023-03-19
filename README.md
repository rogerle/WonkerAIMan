# WonkerAIMan
一站式创建wonker的直播数字人开发环境

### 安装所需环境
安装Conda
Conda 虚拟环境管理系统。 你可以安装 minicoda (选择Python的环境 py>=3.7) . 安装paddlespeech 的依赖:
```shell
conda install -y -c conda-forge sox libsndfile bzip2
```

安装 C++编译环境(如果已经有了，忽略.)

Windows环境你需要安装Visual Studio 来编译 C++.
```text
https://visualstudio.microsoft.com/visual-cpp-build-tools/
```
下载解压nltk_data放入data目录
```shell
wget https://paddlespeech.bj.bcebos.com/Parakeet/tools/nltk_data.tar.gz
unzip nltk_data.tar.gz ./data/nltk_data
```

### 安装时注意依赖包
下载MFA
这里出问题的是一个包需要安装`sudo apt install libopenblas-dev`
然后在mfa目录下的montreal-forced-aligner/lib/thirdparty/bin/libopenblas.so.0要删除。删除后就好了额。




### 安装paddle
没有gpu环境
```text
pip install -r requirements.txt
```
有gpu环境
```text
pip install -r requirements-gpu.txt
```




