#!/bin/bash

# Install OpenCV
cd /tmp
sudo apt-get install -y build-essential
sudo apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install -y python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
git clone https://github.com/opencv/opencv.git opencv
git clone https://github.com/opencv/opencv_contrib.git opencv_contrib
cd opencv
git checkout 3.1.0
cd ../opencv_contrib
git checkout 3.1.0
cd ../opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig
echo "OpenCV installed."

# Install tesseract
sudo apt-get install -y tesseract-ocr
echo "tesseract installed."

# Install PythonMagick
sudo apt-get install -y python-pythonmagick
echo "PythonMagick installed"
