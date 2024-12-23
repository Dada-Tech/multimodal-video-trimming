# multimodal-video-trimming
Video trimming for Educational Content in Low-Production Environments

# Installation

### 1. Create Python3.10 environment

`conda create --name whisperx python=3.10`

`conda activate whisperx`


### 2. Install PyTorch, e.g. for Linux and Windows CUDA11.8:

`conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia`

##### Mac OSX
`conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 -c pytorch`

See other methods [here.](https://pytorch.org/get-started/previous-versions/#v200)


### 3. Install FFMPEG

It also requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) to be installed on your system, which is available from most package managers:
```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```


### 4. Install WhisperX
Partially taken from [WhisperX Installation Guide.](https://github.com/m-bain/whisperx)

`pip install git+https://github.com/m-bain/whisperx.git`

If already installed, update package to most recent commit

`pip install git+https://github.com/m-bain/whisperx.git --upgrade`

##### Note:
Some users face installation failures due to an error with `ctranslate` version not being satisfied.
This can be fixed with the following  

`pip install git+https://github.com/m-bain/whisperx.git@9b9e03c4cc88ddfbbdf5f896918e57dc0298db41`
