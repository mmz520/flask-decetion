import numpy as np
import cv2
from flask import Flask,render_template,Response,request
from flask_caching import Cache
from ctypes import *
import math
import random
import os
import darknet
import postgresql
import time
import threading
from onvif import ONVIFCamera
import zeep
import json

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask('server1')
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

#wsdl_path=os.path.abspath('.')+'/wsdl'

netMain = None
metaMain = None
altNames = None

configPath = "./cfg/yolov4.cfg"
weightPath = "./yolov4.weights"
metaPath = "./cfg/coco.data"

netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)
metaMain = darknet.load_meta(metaPath.encode("ascii"))

darknet_image = darknet.make_image(darknet.network_width(netMain),
    darknet.network_height(netMain),3)


#从数据库获取需要关注的对象
lists= postgresql.operate_postgre_tbl_product("select object_name from follow_list")
#print (lists)
#print('=====================================================================================')

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)
 
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def is_follow_target(find_object):
    for ob in lists:
        if(ob['object_name']==find_object):
            return True
    return False

def need_save(find_object):
    if(not is_follow_target(find_object)): 
        return False
    data=time.strftime('%Y-%m-%d %H',time.localtime(time.time()))
    list_real_time=postgresql.operate_postgre_tbl_product("select target_name from target_information where time like %s and target_name=%s"%("'"+data+"%'","'"+find_object+"'"))
    if(list_real_time==None or len(list_real_time)==0):
        return True
    return False
def get_id():
    max_id=postgresql.operate_postgre_tbl_product("select max(tid) from target_information")
    if(max_id[0]['max']==None):
        return 1
    return max_id[0]['max']+1

def deal_object(find_object):
    if(need_save(find_object)):
        tid="'"+str(get_id())+"'"
        targetName="'"+find_object+"'"
        data="'"+time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))+"'"
        print(data)
        postgresql.operate_set("insert into target_information (tid,target_name,time) values (%s,%s,%s)"%(tid,targetName,data))

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        #print('======================1======================')
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    
        find_object=detection[0].decode()
        deal_object(find_object)
        #print('=======================%s====================='%(find_object))
    return img

def get_img(frame_read):
    frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb,
                                (darknet.network_width(netMain),
                                darknet.network_height(netMain)),
                                interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())

    detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
    image = cvDrawBoxes(detections, frame_resized)
    #print("get_iamging")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

with open(metaPath) as metaFH:
    metaContents = metaFH.read()
    import re
    match = re.search("names *= *(.*)$", metaContents,
                        re.IGNORECASE | re.MULTILINE)
    if match:
        result = match.group(1)
    else:
        result = None

    if os.path.exists(result):
        with open(result) as namesFH:
            namesList = namesFH.read().strip().split("\n")
            altNames = [x.strip() for x in namesList]

class VideoCamera(object):
   
    def __init__(self,enable_detect,way,index):
        # 通过opencv获取实时视频流
        path='rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/'+index
        if(way=='main'):
            path+='01'
        else:
            path+='02'
        
        self.video = cv2.VideoCapture(path) 
        self.enable_detect=enable_detect
        self.out=cv2.VideoWriter('./static/out.avi', cv2.VideoWriter_fourcc(*'XVID'), 5, (640, 480))
        #self.out=cv2.VideoWriter('./static/out.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 5, (640, 480))
        #self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()
    
    
    def get_frame(self):
        #global image
        success, image = self.video.read()
        success, image = self.video.read()
        success, image = self.video.read()
        success, image = self.video.read()
        
        # image = get_img(detection_model, image)
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        if(self.enable_detect=='true'):
            #image = MyThread(get_img_thread, (image,), get_img_thread.__name__).get_result()
            image=get_img(image)
        image = cv2.resize(image, (640, 480))
       # self.out.write(image)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
count=0
def gen(camera):
    count=0
    while True:
        print('线程进行中...')
        count=count+1
        frame = camera.get_frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    count=0
t=None
@app.route('/video_feed/<enable_detect>/<way>/<index>')  # 这个地址返回视频流响应
def video_feed(enable_detect,way,index):
    if(count==0):
        print('线程开启')
        t=MyThread(gen,(VideoCamera(enable_detect,way,index),),gen.__name__)
        t.start()
    #return "为啥啊，干"
    return Response(t.get_result(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')   

class  camera_ptz():
    def __init__(self,ip='192.168.0.64',port=80,account='admin',pwd='abc12345'):
        super().__init__()
        self.ip=ip
        self.port=port
        self.account=account
        self.pwd=pwd
        #self.wsdl=wsdl


def get_camera_ptz(data):
    def dict2cameta(data):
        return camera_ptz(data["ip"],data["port"],data["account"],data["pwd"])
    json_str=json.dumps(json.loads(data))
    ptz_camera=json.loads(json_str,object_hook=dict2cameta)
    return ptz_camera

def get_mycam(data):
    ptz_camera=get_camera_ptz(data)
    mycam=ONVIFCamera(ptz_camera.ip,ptz_camera.port,ptz_camera.account,ptz_camera.pwd)
    return mycam

@app.route('/ptz/<pan>/<pan_speed>/<tilt>/<tilt_speed>/<zoom>/<zoom_speed>',methods=['POST','GET'])
def ptz(pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed):
    if(request.method=='GET'):
        mycam=ONVIFCamera('192.168.0.64',80,'admin','abc12345')
    else:
        mycam=get_mycam(request.data)
    #print('=======================camera infor=====================')
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]

    m_request = ptz.create_type('AbsoluteMove')
    m_request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})

    if m_request.Position is None:
        m_request.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    if m_request.Speed is None:
        m_request.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position

    m_request.Position.PanTilt.x = pan
    m_request.Speed.PanTilt.x = pan_speed

    m_request.Position.PanTilt.y = tilt
    m_request.Speed.PanTilt.y = tilt_speed

    m_request.Position.Zoom = zoom
    m_request.Speed.Zoom = zoom_speed

    ptz.AbsoluteMove(m_request)

    return 'ptz:success'

@app.route('/')
def test():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)