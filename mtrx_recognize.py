#!/usr/bin/env python

import sys
import os

from scipy import stats
import numpy as np
import cv2
import operator as op
import subprocess
import Queue

def get_char((x,y,w,h)):
    curr_segment = im[y: y+h, x: x+w]
    pic_counter = 0
    curr_char = ""
    filename = "curr_char_" + str(pic_counter) + ".png"
    pic_counter += 1
    cv2.imwrite(filename, curr_segment)

    # FNULL = open(os.devnull, 'w')
    tess_path = "tesseract -psm 10 " + filename  + " output nobatch matrix"
    subprocess.call(tess_path, shell=True)
    f = open('output.txt', 'r')
    for line in f:
        curr_char += line.strip()
        
    return curr_char
    

def rectify_rows(arr):
    x_lag, y_lag, w_lag, h_lag = arr[0]
    start = 0
    curr = 0
    curr_group = []
    left_bound = []
    right_bound = []
    
    def smooth(arr, start, curr_group):
        mode = int(stats.mode(curr_group)[0][0])
        # print "mode: " + str(mode)
        # print "start: " + str(start) + ", curr: "+ str(curr)
        for i in range(start, curr):
            arr[i][1] = mode
            # print "curr x: " + str(i)
            # print "ARR: " + str(arr)
        start = curr

        curr_group = []
        curr_group.append(y)
        return (curr, curr_group)
    
    for a in arr:
        # print str(x_lag) + " " + str(y_lag) + " " +str(w_lag) + " " +str(h_lag)
        x,y,w,h = a
        # determine group members
        # print str(y-y_lag)
        if abs(y-y_lag) <= 5:
            curr_group.append(y)
        else:
            # print curr_group
            # smooth group height (for sorting purposes)
            start,curr_group = smooth(arr,start,curr_group)
            x_lag, y_lag, w_lag, h_lag = a
        
        
        curr += 1
        x_lag, y_lag, w_lag, h_lag = a
        
    if curr_group:
        smooth(arr, start, curr_group)
    
    return arr
    

# def numpify_string(master_list):
#     x_last, y_last, w_last, h_last = -1,-1,-1,-1
#     curr_char = ''
#     curr_elem = ""
#     curr_line = ""
#     curr_matrix_string
#
#     numpified_master_list = []
#     curr_matrix_string = ""
#
#     for sublist in master_list:
#         for char_tup in sublist:
#             if x_last == -1:
#                 working_elem += curr_char
#                 x_last = x
#                 y_last = y
#             elif x > x_last and y == y_last:

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


# Rectify the braces and dteremine the character
braces = rectify_rows(braces)
print "RECTUM: " + str(braces)


braces = sorted(braces, key=lambda x : (x[1], x[0]))
print "\n<braces> post rect\n"
for b in braces:
    # if b[1]>200 and b[1]<220:
    b.append(get_char(b))
    print str(b) + " " + str(np.divide(float(b[3]),float(b[2])))


# x_left,y_left,w_left,h_left = braces[0]
# x_right,y_right,w_right,h_right = braces[1]
#
# width = (x_right + w_right) - (x_left + w_left)
# height = h_left
#
# print str(width) + " " + str(height)
# print type(x_left+width)
# print type(y_left+height)
# print "len: " + str(len(braces))
# bounding box for region of single matrix
# cv2.rectangle(im,(x_left+w_left,y_left),(x_left+width,y_left+height),(0,0,255),1)


'''
Do OCR on the segmented images
'''
x_last, y_last, w_last, h_last = -1,-1,-1,-1
matrix_string = ""
working_elem = ""
working_line = ""
counter = 0
pic_counter = 0

entered = False

master_list = []
curr_group = []

left_bounds = [(x,y,w,h,c) for (x,y,w,h,c) in braces if c is '[']
right_bounds = [(x,y,w,h,c) for (x,y,w,h,c) in braces if c is ']']

x_l, y_l = -1,-1
x_r, y_r = -1,-1


while left_bounds and right_bounds:
    x_l,_,_,_,_ = left_bounds[0]
    x_r,_,_,_,_ = right_bounds[0]
    
    curr_group = [(x,y,w,h,c) for (x,y,w,h,c) in braces if c in "0123456789" and x_l < x < x_r]
    
    master_list.append(curr_group)
    
    left_bounds.pop(0)
    right_bounds.pop(0)

print master_list

print left_bounds
print right_bounds

# while ungrouped:
#
# # for b in braces:
#     x, y, w, h = ungrouped[0]
#     # print ungrouped
#
#     curr_char = ""
#     curr_segment = im[y: y+h, x: x+w]
#     filename = "curr_char_" + str(pic_counter) + ".png"
#     pic_counter += 1
#     cv2.imwrite(filename, curr_segment)
#
#     # FNULL = open(os.devnull, 'w')
#     tess_path = "tesseract -psm 10 " + filename  + " output nobatch matrix"
#     subprocess.call(tess_path, shell=True)
#     f = open('output.txt', 'r')
#
#     for line in f:
#         curr_char += line.strip()
#     # print "not quite: " + str(num)
#     print curr_char
#     if curr_char in ("[]"):
#         # print "bound"
#         if curr_char == "[":
#             left_bounds.append(ungrouped.pop(0))
#             # if x_l == -1:
#             #     x_l,_,_,_ = left_bounds.pop(0)
#         elif curr_char == "]":
#             right_bounds.append(ungrouped.pop(0))
#             # if x_r == -1:
#             #     x_r,_,_,_  = right_bounds.pop(0)
#
#     print "bounds: " + str(x_l) + " " + str(x_r)
#
#     if curr_char in ("0123456789")  and x_l < x < x_r:
#         entered = True
#         # print "here"
#         # print "curr_char: " + curr_char
#         # print "working elem: " + working_elem
#         # print "working line: " + working_line
#         print "CURR CHAR: " + curr_char + " <<y last: " + str(y_last) + ", " + "y curr: " + str(y) + ">>"
#         if counter == 0:
#             print "BASE CASE"
#             working_elem += curr_char
#             x_last = x
#             y_last = y
#             print "working: " + working_elem
#         elif y == y_last and 1.2*(x_last + w_last) >=  x:
#             print "SECOND CASE"
#             working_elem += curr_char
#             x_last = x
#             y_last = y
#             print "working: " + working_elem
#         elif y == y_last:
#             print "THIRD CASE"
#             working_line += working_elem + " "
#             working_elem = ""
#             working_elem += curr_char
#         elif y != y_last:
#             print "FOURTH CASE"
#             matrix_string += working_line + "; "
#             working_line = ""
#         # counter += 1
#         x_last, y_last, w_last, h_last = ungrouped[0]
#
#
#     # print str(curr_char)
#     # matrix_string += str(curr_char)
#
#     # if num.isdigit() and counter > 1:
#     #     print "reaches"
#     #     if counter != 0 and y >= y_last + 65:
#     #         matrix_string += "; " + str(num) + " "
#     #         print num
#     #         num = ""
#     #     elif counter == 0 or 1.2*(x_last + w_last) <  x:
#     #         matrix_string += str(num) + " "
#     #         print num
#     #         num = ""
#     # else:
#     #     matrix_string += str(num)
#
#     # x_last, y_last, w_last, h_last = ungrouped[0]
#     counter += 1
#     # curr_char = ""
#     subprocess.call('rm output.txt', shell=True)
#     # if entered is True:
# #         ungrouped.append((x_last,y_last,w_last,h_last))
# #         entered = False
#     ungrouped.pop(0)
#
# print "left bounds: " + str(left_bounds)
# print "right bounds: " + str(right_bounds)
# print "mtrx: "  + matrix_string

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
