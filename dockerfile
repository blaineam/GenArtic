FROM nvidia/cuda:11.0.3-base-ubuntu20.04

# Upgrade installed packages

RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.7
# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

RUN apt install -y curl

CMD ['/bin/bash']
