#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
2014/08/18 jiaqianghuai: create this code
"""

__author__ = 'hzjiaqianghuai'
__version__ = '0.0.08.18'
__description__ ='create this code'

import os
import time
import math
import numpy as np
import cv2
import image

DEBUG = os.getenv('DEBUG') == 'true'

def method_test(datadir, query_path, outfiledir):
    out_image_list, time_list, avg_time = [], [], 0.0
    file_name = os.path.basename(query_path)
    query_name = file_name.split('.')[0]
    if os.path.exists(outfiledir) == 0: #create new file
        os.mkdir(outfiledir)
    outfile_path = os.path.join(outfiledir,'Adjust')
    if os.path.exists(outfile_path) == 0: #create new file
        os.mkdir(outfile_path)
    else:
        for name in os.listdir(outfile_path): #clear
            os.remove(os.path.join(outfile_path,name))
    if DEBUG: print outfile_path
    sum_time, count = 0.0, 0
    for lists in os.listdir(datadir):
        if DEBUG: print lists
        file_path = os.path.join(datadir,lists)
        if DEBUG: print file_path
        outfile = os.path.join(outfile_path,file_name + '_' + lists)       
        starttime1 = time.clock()
        pts = image.locate_image(file_path, query_path, outfile, 0.3)
        endtime1 = time.clock()
        if pts: 
            if DEBUG: print pts
            time2 = round(endtime1 - starttime1,4)
            sum_time = sum_time + time2
            count = count + 1 
            out_image_list.append(outfile)
            time_list.append(str(time2))
    if count < 1:
        avg_time = 0.0
    else:
        avg_time = round(sum_time/count, 4)
    return out_image_list, time_list, avg_time

def image_save(image_path, image_name, match_error_outfile):    
    if os.path.exists(image_path):
        img = cv2.imread(image_path)
        outfile_path = os.path.join(match_error_outfile,image_name)
        cv2.imwrite(outfile_path, img)
        #os.remove(image_path)

def image_list_save(image_list, match_error_outfile):
    for image_path in image_list:
        image_name = os.path.basename(image_path)
        image_save(image_path, image_name, match_error_outfile)