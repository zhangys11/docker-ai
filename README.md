# Abstract

This is a self-developed docker image to provide a common env for deep learning and data science research.

Features of image:
1. GUI in browser (powered by dorowu/ubuntu-desktop-lxde-vnc)
2. auto-sklearn
3. flask-based AI apps: Q2 and C3

# Quickstart

`docker pull zhangyinsheng/ai:bionic`

`docker run --name ubvnc -v %cd%:/host/ -p 5900:5900 -p 6080:80 -p 8888:8888 zhangyinsheng/ai:bionic`

# Build

The building process of this image is painful (due to many version conflicts and package incompatible issues). I wrote down the full process for future reference.

## Pull the base image 

> docker pull dorowu/ubuntu-desktop-lxde-vnc:bionic

Other Ubuntu flavors are available by the tags:

    focal: Ubuntu 20.04 (latest)
    focal-lxqt: Ubuntu 20.04 LXQt
    bionic: Ubuntu 18.04
    bionic-lxqt: Ubuntu 18.04 LXQt


After download, create a container to test the image: 

> docker run --name ubvnc -p 6080:80 -p 5900:5900 dorowu/ubuntu-desktop-lxde-vnc:bionic

Then you can access http://127.0.0.1:6080/ in web browser. A vnc remote desktop should show up.

## Install Packages

Open a terminal inside the vnc desktop or directly launch the CLI from the docker container.

Then run the following commands:

> bash

> apt update 

    You may also use apt-get, but generally the apt tool is favored. apt merges functionalities of apt-get and apt-cache

> apt install python3-pip build-essential swig python3-dev nodejs npm git nano gedit python-is-python3

> apt install libjpeg-dev zlib1g-dev 
 
    pillow / PIL needs these two packages

> apt install lsof

    We will use lsof to kill processes by the port number.

> pip3 install tensorflow==1.14.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

> pip3 install keras==2.3.1

> pip3 install h5py==2.10.0 --force-reinstall

    tf 1.X, keras 2.3.1 and h5py 2.10.0 have better compatibility. Newer versions will raise error for legacy py codes.

> pip3 install auto-sklearn 

    for poor network, use: pip3 install --upgrade --default-timeout=100000 auto-sklearn

> pip3 install pillow  -i https://pypi.tuna.tsinghua.edu.cn/simple

    During the installation, lazy_import may raise exception. Use the following solution:

> git clone --recurse-submodules http://github.com/mnmelo/lazy_import.git
> cd lazy_import
> nano setup.py # modify the code to skip reading README.rst
> pip install -e .

Test the autosklearn can be imported properly.

> python3
  >> import autosklearn

## Copy Host Files

Copy app codes to the container

> docker cp "host_path_to\Q2_Flask" ubvnc:/root/
> docker cp "host_path_to\C3_Flask" ubvnc:/root/

    The default working directory is /root.

Similarly, copy the three app startup scripts (*.sh) to the container's desktop.

## Publish to Docker Hub

> docker commit ubvnc zhangyinsheng/ai:bionic

> docker push zhangyinsheng/ai:bionic

# Run

> docker run --name ubvnc -v %cd%:/host/ -p 5900:5900 -p 6080:80 -p 8888:8888 zhangyinsheng/ai:bionic

On Linux host, should change `%cd%` to `$(pwd)`  
`-v %cd%:/host/` links host home to the container, for file access and sharing convenience.

Once inside the vnc desktop, you will see three sh files:

1. jupyter notebook with autosklearrn support.sh 

    This will start up a jupyter notebook on port 8888. The default work dir is /root. autosklearn is supported.

2. Fundus Q2 Classifier.sh

    This will start up a web based fundus image qualifier on port 5002:
    <img src='Q2.png'>
    This app judges whether an image is a qualified fundus image. This easy classification task has an accuracy of nearly 100%.

3. Fundus C3 Classifier.sh

    This will start up a web based fundus image classification on port 5003:
    <img src='C3.png'>
    This is a three-class classification task (normal, stage1-2, stage 3-4). The model's accuracy is about 88.8%. We are still working on this model to improve its performance.

4. Users may implement and deploy their own web-based AI apps by reusing this docker image.

