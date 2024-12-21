# multimodal-video-trimming
Video trimming for Educational Content in Low-Production Environments

# Installation
Partially taken from [WhisperX Installation Guide.](https://github.com/m-bain/whisperx)

### 1. Create Python3.10 environment

`conda create --name whisperx python=3.10`

`conda activate whisperx`


### 2. Install PyTorch, e.g. for Linux and Windows CUDA11.8:

`conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia`

##### Mac OSX
`conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 -c pytorch`

See other methods [here.](https://pytorch.org/get-started/previous-versions/#v200)

### 3. Install this repo

`pip install git+https://github.com/m-bain/whisperx.git`

If already installed, update package to most recent commit

`pip install git+https://github.com/m-bain/whisperx.git --upgrade`

If wishing to modify this package, clone and install in editable mode:
```
$ git clone https://github.com/m-bain/whisperX.git
$ cd whisperX
$ pip install -e .
```

Note: Some users face installation failures due to an error with `ctranslate` version not being satisfied.  
Use `pip install git+https://github.com/m-bain/whisperx.git@9b9e03c4cc88ddfbbdf5f896918e57dc0298db41`
