doc2text
========

.. image:: https://travis-ci.org/jlsutherland/doc2text.svg?branch=master
   :target: https://travis-ci.org/jlsutherland/doc2text

.. image:: https://badge.fury.io/py/doc2text.svg
    :target: https://badge.fury.io/py/doc2text

About `doc2text`
----------------
Developing the text corpora can be a massive pain in the butt. Much of the text data we are interested in as economists, political scientists, historians   `doc2text` was created because as a researcher,

Installation
------------
To install the `doc2text` package, simply:

.. code-block:: python
   pip install doc2text

`doc2text` relies on the the `OpenCV <http://github.com/opencv/opencv>`_ and `tesseract <http://github.com/tesseract-ocr/tesseract>`_ libraries. To execute the quick-install script:

.. code-block:: bash
   curl https://raw.githubusercontent.com/jlsutherland/doc2text/master/install_opencv.sh | sh

To install OpenCV on Ubuntu 16.04 Xenial:

.. code-block:: bash
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
   sudo apt-get install tesseract-ocr
