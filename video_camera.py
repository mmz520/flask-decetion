import cv2
from get_derection import get_img
import time
from ptz import paste
from PIL import Image


class VideoCamera(object):
   
    def __init__(self,enable_detect,way,index):
        # 通过opencv获取实时视频流
        path='rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/'+index
        if(way=='main'):
            path+='01'
        else:
            path+='02'
        
        if(index==-1 or index=='-1'):
            path='bird.mp4'
        
        #fps = 5
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #fourcc = cv2.VideoWriter_fourcc('F','L','V','1')
        self.video = cv2.VideoCapture(path) 
        self.enable_detect=enable_detect
        #self.out=cv2.VideoWriter('./static/out.flv',fourcc,fps,(640,480),True)

    def __del__(self):
        self.video.release()
        #self.out.release()
    
    def get_frame(self):
        #global image
        success, image = self.video.read()
        success, image = self.video.read()
        success, image = self.video.read()
        success, image = self.video.read()
        
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        if(self.enable_detect=='true'):
            #print("==========================")
            image=get_img(image)
            
        #self.out.write(image)
        #image=paste(Image.fromarray(image),cv2.imread('test.png',cv2.IMREAD_UNCHANGED))
        ret, jpeg = cv2.imencode('.jpg', image)
        #time.sleep(1/30)
        return jpeg.tobytes()