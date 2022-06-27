FROM nvidia/cuda:11.0.3-base-ubuntu20.04

# Upgrade installed packages
RUN apt update && apt upgrade -y
RUN apt install -y build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev

RUN wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz

RUN tar xf Python-3.7.0.tar.xz

RUN cd Python-3.7.0


RUN ./configure --enable-optimizations

RUN make -j 8

RUN make altinstall

# Register the version in alternatives


RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

# Upgrade pip to latest version
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py

RUN mkdir -p /content

WORKDIR /content

RUN git clone --recursive --branch release https://github.com/pixray/pixray

RUN echo "gradio" >> pixray/requirements.txt

RUN pip install -r pixray/requirements.txt

RUN pip uninstall -y torch torchvision torchaudio

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113

RUN pip install basicsr 

RUN pip install b2sdk emails python-dotenv

RUN pip uninstall -y tensorflow

RUN git clone https://github.com/blaineam/diffvg

RUN cd ./diffvg && git submodule update --init --recursive && cd ..

RUN cd ./diffvg && CUDA_TOOLKIT_ROOT_DIR=CUDA_PATH DIFFVG_CUDA=1 python setup.py install && cd ..

RUN pip freeze | grep torch

RUN mkdir -p /content/models/

RUN wget -q --show-progress -nc -O /content/models/vqgan_coco.yaml https://dl.nmkd.de/ai/clip/coco/coco.yaml

RUN wget -q --show-progress -nc -O /content/models/vqgan_coco.ckpt https://dl.nmkd.de/ai/clip/coco/coco.ckpt

RUN apt update && apt install -y ffmpeg

ADD genartic.py /content/

ENV PYTHONUNBUFFERED=1

CMD [ "python", "./genartic.py" ]
