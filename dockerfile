# Uses CUDA 11 Ubuntu Base Image
FROM nvidia/cuda:11.0.3-base-ubuntu20.04
# Setup Apt dependencies including Python
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.7* ffmpeg curl vim wget git
RUN apt clean autoclean && \
    apt autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7
# Upgrade pip to latest version
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py
# Setup working directory
RUN mkdir -p /content
WORKDIR /content
# Pull primary dependency Pixray
RUN git clone --recursive --branch release https://github.com/pixray/pixray
# Add UI library to requirements so Pip can build an accurate dependency graph
RUN echo "gradio" >> pixray/requirements.txt
RUN pip install -r pixray/requirements.txt
# Switch the pytorch version to one that works with CUDA 11
RUN pip uninstall -y torch torchvision torchaudio
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
# Uninstall tensorflow because it is not used
RUN pip uninstall -y tensorflow
# Install GenArtic Python Module Dependencies
RUN pip install boto3 emails python-dotenv
# Create location to store ML models
RUN mkdir -p /content/models/
# Include the code for GenArtic
ADD genartic.py /content/
# Run the service
ENV PYTHONUNBUFFERED=1
CMD [ "python", "./genartic.py" ]
