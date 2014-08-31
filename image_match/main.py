#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'jiaqianghuai'
__version__ = '0.2.08.31'
__description__ ='upload this code'


import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, redirect, url_for, request
import cv2
import image
import search

app = Flask(__name__)
app.config.from_object(__name__)

UPLOAD_FOLDER = 'static/data/uploads'
RESULTS_FOLDER = 'static/data/results'
DATASET_FOLDER = 'static/data/dataset'
OUTFILE_FOLDER = 'static/data/outfile'
MATCH_ERROR_FOLDER = 'static/data/match_error_results'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['DATASET_FOLDER'] = DATASET_FOLDER
app.config['OUTFILE_FOLDER'] = OUTFILE_FOLDER
app.config['MATCH_ERROR_FOLDER'] = MATCH_ERROR_FOLDER

ALLOWED_EXTENSIONS = ['bmp', 'png', 'jpg', 'jpeg', 'gif']
Image_List = []
IP_List = []

@app.route("/")
def index():
    ip = request.headers.get('X-Real-Ip', request.remote_addr)
    num = len(IP_List)
    if 0 < num:
        for i in range(num):
            if ip == IP_List[num-1-i]: 
                Image_List.pop(num-1-i)
                IP_List.pop(num-1-i)
    print Image_List, IP_List
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            now = datetime.now()
            filename = os.path.join(UPLOAD_FOLDER, "%s.%s" % 
                (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), secure_filename(file.filename)))
            file.save(filename)
            Image_List.append(filename)
            real_ip = request.headers.get('X-Real-Ip', request.remote_addr)
            IP_List.append(real_ip)
            print "48: ", IP_List
            print "49: ", Image_List       
            return jsonify({"success":True})

@app.route('/match', methods=['GET'])
def match():
    ip = request.headers.get('X-Real-Ip', request.remote_addr)
    print "55: ", ip
    if request.method == 'GET':
        if len(Image_List) <= 1:
            if (len(Image_List) == 1 and IP_List[-1] == ip):
                del Image_List[:]
                del IP_List[:]
            return render_template("index.html") 
        elif len(Image_List) == 2:
            if IP_List[0] == ip and IP_List[1] == ip:
                image1 = Image_List[0]
                image2 = Image_List[1]
                del Image_List[:]
                del IP_List[:]
                pts, match_time, fname = image_match(image1, image2)
                if pts:
                    print "name: ", fname
                    return render_template('match.html', img=fname, center=pts,
                                            match_time=match_time)
                else:
                    image_name = os.path.basename(fname)
                    search.image_save('static/img/sorry.jpg', image_name, RESULTS_FOLDER)
                    return render_template('match.html', img=fname, 
                                            center=None, match_time=match_time)
            else:
                real_ip0 = IP_List[0]
                real_ip1 = IP_List[1]
                if ip == real_ip0:
                    del Image_List[0]
                    del IP_List[0]
                elif ip == real_ip1:
                    del Image_List[1]
                    del IP_List[1]
                return render_template("index.html")
        elif 2 < len(Image_List):
            count = 0
            index = []
            for i in range(len(Image_List)):
                if IP_List[i] == ip:
                    count = count + 1
                    index.append(i)
            if count == 1:
                del Image_List[index[0]]
                del IP_List[index[0]]
                return render_template("index.html")
            elif count == 2:
                image1 = Image_List[index[0]]
                image2 = Image_List[index[1]]
                del Image_List[index[0]]
                del Image_List[index[1]]
                del IP_List[index[0]]
                del IP_List[index[1]]                
                pts, match_time, fname = image_match(image1, image2)
                if pts:
                    print "name: ", fname
                    return render_template('match.html', img=fname, center=pts,
                                            match_time=match_time)
                else:
                    image_name = os.path.basename(fname)
                    search.image_save('static/img/sorry.jpg', image_name, RESULTS_FOLDER)
                    return render_template('match.html', img=fname, 
                                            center=None, match_time=match_time)
            elif 3 <= count:
                print "116: ", count, len(index),index
                for i in range(count):
                    Image_List.pop(index[count-1-i])
                    IP_List.pop(index[count-1-i])
                return render_template("index.html")
        else:
             return render_template("index.html")

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        image_list = request.form.getlist('Match_Err')
        search.image_list_save(image_list, MATCH_ERROR_FOLDER)
        #flash('Thanks for your feedback')
        return render_template('feedback.html')


                                        
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    
def image_match(image1, image2):
    img_temp = cv2.imread(image1)
    img_src = cv2.imread(image2)
    width_temp, width_src = img_temp.shape[1], img_src.shape[1]
    if width_temp <= width_src:
        fname_temp = image1
        fname_src = image2
    else:
        fname_temp = image2
        fname_src = image1                
    query_name = os.path.basename(fname_temp)
    target_name = os.path.basename(fname_src)
    fname = os.path.join(RESULTS_FOLDER,"%s_%s" % (query_name, target_name.split('.', 1)[1]))
    starttime = time.clock()
    pts = image.locate_one_image(fname_src, fname_temp, fname)
    endtime = time.clock()
    match_time = round(endtime - starttime,4)
    return pts, match_time, fname

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
