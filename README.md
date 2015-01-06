MatrixHelper
============

a library to extract matrices from images and perform matrix operations

### DONE (1/5/14)
* parse in images of matrices with integers

### TODO
* handle floating point numbers
* handle operators
* phone port

### Dependencies

* Python 2.7.6
* NumPy 1.8.0
* OpenCV 2.4.9
* Tesseract 3.02 (and its dependencies)

#### An IMPORTANT note
In your tessdata/configs folder, be sure to put the "matrix" file.  If you haven't already, you can set the TESSDATA path (ie, the folder containing your "tessdata" folder) with the following command (assuming a nix system):
```
export TESSDATA_PREFIX="<tessdata path>"
```
My TESSDATA path, for instance, is "/usr/local/share/"
