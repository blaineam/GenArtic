FROM python:3.7

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

RUN git clone https://github.com/pixray/diffvg

RUN cd ./diffvg && git submodule update --init --recursive && cd ..

RUN cd ./diffvg && DIFFVG_CUDA=1 python setup.py install && cd ..

RUN pip freeze | grep torch

RUN mkdir -p /content/models/

RUN wget -q --show-progress -nc -O /content/models/vqgan_coco.yaml https://dl.nmkd.de/ai/clip/coco/coco.yaml

RUN wget -q --show-progress -nc -O /content/models/vqgan_coco.ckpt https://dl.nmkd.de/ai/clip/coco/coco.ckpt

RUN apt update && apt install -y ffmpeg

ADD genartic.py /content/

ENV PYTHONUNBUFFERED=1

CMD [ "python", "./genartic.py" ]
