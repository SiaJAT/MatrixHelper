#!/usr/bin/env python

import sys
import os

from scipy import stats
import numpy as np
import cv2
import operator as op
import subprocess
import Queue


im = cv2.imread(str(sys.argv[1]).strip())
im3 = im.copy()
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(5,5),0)
thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)

contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

contours_dims = []
for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    contours_dims.append((cnt,w,h))

contours_dims = sorted(contours_dims, key=lambda x : (-cv2.contourArea(x[0]),-x[1],-x[2]))
for cnt in contours_dims:
    print str(cv2.contourArea(cnt[0])) + " " + str(cnt[1]) + " " + str(cnt[2]) 


braces = []
for x in range(0, len(contours)):
    x,y,w,h = cv2.boundingRect(contours_dims[x][0])
    braces.append([x,y,w,h])
    print str(x) + " " +  str(y)
    # if y>200 and y <220:
    # cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),2)

braces = sorted(braces, key=lambda x : (x[1], x[0]))

print "\n<braces>\n"
for b in braces:
    # if b[1]>200 and b[1]<220:
    print b

x_lag, y_lag, w_lag, h_lag = braces[0]
start = 0
curr = 0
curr_group = []
left_bound = []
right_bound = []
'''
Old sorting code
'''
for b in braces:
    # print str(x_lag) + " " + str(y_lag) + " " +str(w_lag) + " " +str(h_lag)
    x,y,w,h = b
    # determine group members
    if start > -1:
        if abs(y-y_lag) <= 5:
            curr_group.append(y)
        else:
            # smooth group height (for sorting purposes)
            mode = int(stats.mode(curr_group)[0][0])
            # print "mode: " + str(mode)
            # print "start: " + str(start) + ", curr: "+ str(curr)
            for i in range(start, curr):
                braces[i][1] = mode
            start = curr

            curr_group = []
            curr_group.append(y)

    curr += 1
    x_lag, y_lag, w_lag, h_lag = b

braces = sorted(braces, key=lambda x : (x[1], x[0]))
print "\n<braces> post rect\n"
for b in braces:
    # if b[1]>200 and b[1]<220:
    print str(b) + " " + str(np.divide(float(b[3]),float(b[2])))


x_left,y_left,w_left,h_left = braces[0]
x_right,y_right,w_right,h_right = braces[1]

width = (x_right + w_right) - (x_left + w_left)
height = h_left

print str(width) + " " + str(height)
print type(x_left+width)
print type(y_left+height)
print "len: " + str(len(contours))
# bounding box for region of single matrix
# cv2.rectangle(im,(x_left+w_left,y_left),(x_left+width,y_left+height),(0,0,255),1)


'''
Do OCR on the segmented images
'''

# x_last, y_last, w_last, h_last = None,None,None,None
matrix_string = ""
curr_char = ""
counter = 0
pic_counter = 0
left_bounds = Queue.Queue()
right_bounds = Queue.Queue()

# while ungrouped:

for b in braces:
    x, y, w, h = b

    curr_segment = im[y: y+h, x: x+w]
    filename = "curr_char_" + str(pic_counter) + ".png"
    pic_counter += 1
    cv2.imwrite(filename, curr_segment)

    # FNULL = open(os.devnull, 'w')
    tess_path = "tesseract -psm 10 " + filename  + " output nobatch matrix"
    subprocess.call(tess_path, shell=True)
    f = open('output.txt', 'r')
    
    for line in f:
        curr_char += line.strip()
    # print "not quite: " + str(num)
    
    if curr_char in ("[]"):
        print "bound"
        if curr_char == "[":
            left_bounds.put('[')
        else:
            right_bounds.put(']')
    
    print str(curr_char)
    matrix_string += str(curr_char)
    
    # if num.isdigit() and counter > 1:
    #     print "reaches"
    #     if counter != 0 and y >= y_last + 65:
    #         matrix_string += "; " + str(num) + " "
    #         print num
    #         num = ""
    #     elif counter == 0 or 1.2*(x_last + w_last) <  x:
    #         matrix_string += str(num) + " "
    #         print num
    #         num = ""
    # else:
    #     matrix_string += str(num)
    
    x_last, y_last, w_last, h_last = b
    counter += 1
    curr_char = ""
    subprocess.call('rm output.txt', shell=True)
    
print "mtrx: "  + matrix_string

# # CROPPING NOTE: its img[y: y + h, x: x + w]
# # segment = im[233:275, 103:164]
# # segment = im[85:366, 81:102]
# segment = im[85:366, 389:419]
#
# # cv2.imshow("uh", segment)
# cv2.imwrite("yeah.png", segment)
#
# # FNULL = open(os.devnull, 'w')
# subprocess.call('tesseract -psm 7 yeah.png output', shell=True)
# f = open('output.txt', 'r')
# num = ""
# for line in f:
#     num += line.strip()
#
# print num.isdigit()
# subprocess.call('rm output.txt', shell=True)
# cv2.imshow("im", im)
#
# # cv2.imwrite("bounded_sample.png",im)
#
# key = cv2.waitKey(0)


if cv2.waitKey(1) & 0xFF == ord("q"):  # (escape to quit)
    cv2.destroyAllWindows()
    sys.exit()
