doc2text
========

.. image:: https://travis-ci.org/jlsutherland/doc2text.svg?branch=master
   :target: https://travis-ci.org/jlsutherland/doc2text

.. image:: https://badge.fury.io/py/doc2text.svg
    :target: https://badge.fury.io/py/doc2text

|

.. image:: docs/assets/images/news-button.png
   :alt: Signup for Announcements
   :target: http://eepurl.com/celDRz
   :width: 200px

|


`doc2text` extracts higher quality text by fixing common scan errors
--------------------------------------------------------------------
Developing text corpora can be a massive pain in the butt. Much of the text data we are interested in as scientists are locked away in pdfs that are poorly scanned. These scans can be off kilter, poor resolution, have a hand in them... and if you OCR these scans without fixing these errors, the OCR doesn't turn out so well. `doc2text` was created to help researchers fix these errors and extract the highest quality text from
their pdfs as possible.


`doc2text` is super duper alpha atm
-----------------------------------
`doc2text` is developed and tested on Ubuntu 16.04 LTS Xenial Xerus. We do not pretend to serve all operating systems at the moment because that would be irresponsible. Please use this software with a huge grain of salt. We are currently working on:

- Increasing the responsiveness of the text block identifier.
- Optimizing the binarization for tesseract detection.
- Identifying text in multiple columns (right now, treats as one big column).
- Handling tables.
- Many other optimizations.

Support and Contributions
-------------------------
If you have feedback or would like to contribute, *please, please* submit a pull request or contact me at `joseph dot sutherland at columbia dot edu`.


Installation
------------
To install the `doc2text` package, simply:

.. code-block:: python

   pip install doc2text

`doc2text` relies on the `OpenCV <http://github.com/opencv/opencv>`_, `tesseract <http://github.com/tesseract-ocr/tesseract>`_, and `PythonMagick` libraries. To execute the quick-install script, which installs OpenCV, tesseract, and PythonMagick:

.. code-block:: bash

   curl https://raw.githubusercontent.com/jlsutherland/doc2text/master/install_deps.sh | bash

Manual installation
~~~~~~~~~~~~~~~~~~~
To install OpenCV manually:

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

To install tesseract manually:

.. code-block:: bash

   sudo apt-get install tesseract-ocr

To install PythonMagick manually:

.. code-block:: bash

   sudo apt-get install python-pythonmagick

Example usage
-------------

.. code-block:: python

   import doc2text

   # Initialize the class.
   doc = doc2text.Document()

   # You can pass the lang (as 3 letters code) to the class to improve accuracy
   # On ubuntu it requires the package tesseract-ocr-$lang$
   # On other OS, see https://github.com/tesseract-ocr/langdata
   doc = doc2text.Document(lang="eng")

   # Read the file in. Currently accepts pdf, png, jpg, bmp, tiff.
   # If reading a PDF, doc2text will split the PDF into its component pages.
   doc.read('./path/to/my/file')

   # Crop the pages down to estimated text regions, deskew, and optimize for OCR.
   doc.process()

   # Extract text from the pages.
   doc.extract_text()
   text = doc.get_text()

Big thanks
----------

doc2text would be nothing without the open-source contributions of:

- `@danvk <http://github.com/danvk>`_
- `@jrosebr1 <http://github.com/jrosebr1>`_
- Countless stackoverflow posts and comments.
