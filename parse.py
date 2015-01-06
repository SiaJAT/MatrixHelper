#!/usr/bin/env python

import sys
import os

from scipy import stats
import numpy as np
import cv2
import subprocess

# global pic_counter = 0

def get_char((x,y,w,h)):
    curr_segment = im[y: y+h, x: x+w]
    pic_counter, curr_char = 0, ""
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
    

def numpify_string(master_list):
    x_last, y_last, w_last, h_last = -1,-1,-1,-1
    curr_char = ''
    curr_elem = ""
    curr_line = ""
    curr_matrix_string = ""

    numpified_master_list = []
    curr_matrix_string = ""

    for sublist in master_list:
        for char_tup in sublist:
            x,y,w,h,curr_char = char_tup
            # print curr_char
            if x_last == -1:
                print "first character"
                curr_elem += curr_char
            elif x > 1.025*(x_last + w_last) and y == y_last:
                print "SAME LINE, NEW ELEM"
                curr_line += curr_elem + " "
                curr_elem = ""
                curr_elem += curr_char
            elif x <= 1.025*(x_last + w_last) and y == y_last:
                print "SAME LINE, SAME ELEM"
                curr_elem += curr_char
            else:
                print "NEW LINE"
                curr_line += curr_elem + "; "
                curr_elem = ""
                curr_elem += curr_char


            x_last, y_last, w_last, h_last = x,y,w,h
                
        if curr_elem:
            curr_line += curr_elem
            curr_matrix_string += curr_line     
        
        numpified_master_list.append(curr_matrix_string)
        x_last, y_last, w_last, h_last = -1,-1,-1,-1
        curr_char = ''
        curr_elem = ""
        curr_line = ""
        curr_matrix_string = ""
        
    return numpified_master_list
    
if __name__ == '__main__':
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
    # for cnt in contours_dims:
        # print str(cv2.contourArea(cnt[0])) + " " + str(cnt[1]) + " " + str(cnt[2])


    braces = []
    for x in range(0, len(contours)):
        x,y,w,h = cv2.boundingRect(contours_dims[x][0])
        braces.append([x,y,w,h])
        # print str(x) + " " +  str(y)
        # if y>200 and y <220:
        #   cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,255),2)

    braces = sorted(braces, key=lambda x : (x[1], x[0]))

    # print "\n<braces>\n"
    # for b in braces:
    #     # if b[1]>200 and b[1]<220:
    #     print b

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



    # Filter out bounding braces (# of brace pairs == number of matrices)
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


    # Reconstruct the matrices
    while left_bounds and right_bounds:
        x_l,_,_,_,_ = left_bounds[0]
        x_r,_,_,_,_ = right_bounds[0]
    
        curr_group = [(x,y,w,h,c) for (x,y,w,h,c) in braces if c in "0123456789" and x_l < x < x_r]
    
        master_list.append(curr_group)
    
        left_bounds.pop(0)
        right_bounds.pop(0)

    # print the matrix elements that are ordered
    for l in master_list:
        print "\n"
        for e in l:
            print e

    # generate numpy string to make matrix
    master = numpify_string(master_list)
    print master

    # create list of matrices
    matrix_return = [np.matrix(x) for x in master]
    for m in matrix_return:
        print m

    if cv2.waitKey(1) & 0xFF == ord("q"):  # (escape to quit)
        cv2.destroyAllWindows()
        sys.exit()

