import queue
import threading
import cv2 as cv
import subprocess as sp
from get_derection import get_img
import numpy as np
import time
#import darknet

# netMain = None
# metaMain = None
# altNames = None

# configPath = "./cfg/yolov4.cfg"
# weightPath = "./yolov4.weights"
# metaPath = "./cfg/coco.data"

# darknet_image = darknet.make_image(darknet.network_width(netMain),
#     darknet.network_height(netMain),3)

# netMain = darknet.load_net_custom(configPath.encode(
#             "ascii"), weightPath.encode("ascii"), 0, 1)
# metaMain = darknet.load_meta(metaPath.encode("ascii"))


class Live(object):
    def __init__(self):
        self.frame_queue1 = queue.Queue()
        self.frame_queue2 = queue.Queue()
        self.frame_queue3 = queue.Queue()
        self.command = ""
        # 自行设置
        self.rtmpUrl = "rtmp://192.168.0.236:1935/live/camera1"
        self.camera_path = "rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/201"
        #self.camera_path = "rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101"
        self.cap = cv.VideoCapture(self.camera_path)
        self.laster=np.zeros((int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)),int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),3),np.uint8)


    def read_frame(self):
        #cap = cv.VideoCapture(self.camera_path)
        print("开启推流")
        # Get video information
        fps = int(self.cap.get(cv.CAP_PROP_FPS))
        width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        # ffmpeg command
        self.command = ['ffmpeg',
                '-y',
                '-f', 'rawvideo',
                '-vcodec','rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(width, height),
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-f', 'flv', 
                self.rtmpUrl]

        count=0
        while(self.cap.isOpened()):
            imgs=[]
            for index in range(60):
                ret,frame=self.cap.read()
                imgs.append(frame)
            
            self.frame_queue2.put(imgs[len(imgs)-1])
            for index in range(len(imgs)):
                self.frame_queue1.put(imgs[index])
                    
            #ret, frame=self. cap.read()
            #ret, frame9 =self. cap.read()
            if not ret:
                print("Opening camera is failed")
                break
            # count+=1 
            # self.frame_queue1.put(frame) 
            # if(count==10):
            #     self.frame_queue2.put(frame)
            #     count=0


    def detection_push(self):
        while True:
            if not self.frame_queue2.empty():
                img=self.frame_queue2.get()
                frame=get_img(img)
                self.frame_queue3.put((frame,img))


    def m_print(self):
        while True:
            print("queue1:"+str(self.frame_queue1.qsize()))
            print("queue2:"+str(self.frame_queue3.qsize()))
            print("queue3:"+str(self.frame_queue3.qsize()))
            time.sleep(3)


    def push_frame(self):
        # 防止多线程时 command 未被设置
        while True:
            if len(self.command) > 0:
                # 管道配置
                p = sp.Popen(self.command, stdin=sp.PIPE)
                break
        while True:
            if not self.frame_queue1.empty():
                img1=self.frame_queue1.get()
                if not self.frame_queue3.empty():
                    imgs=self.frame_queue3.get()
                    if (img1==imgs[1]).all():
                        print(self.frame_queue3.qsize())
                        self.laster=imgs[0]
                    else:
                        queue3=queue.Queue()
                        for index in range(self.frame_queue3.qsize()+1):
                            if(index==0):
                                queue3.put(imgs)
                            else:
                                queue3.put(self.frame_queue3.get())
                        self.frame_queue3=queue3
                frame=cv.add( self.laster,img1)
                p.stdin.write(frame.tostring())

        # while True:    
        #     if not self.frame_queue3.empty() and not self.frame_queue1.empty():
        #         self.laster=self.frame_queue3.get()
        #         frame=cv.add( self.laster,self.frame_queue1.get())
        #         #print(self.frame_queue2.get().shape)
        #         p.stdin.write(frame.tostring())
        #     elif not self.frame_queue1.empty():
        #         frame=cv.add( self.laster,self.frame_queue1.get())
        #         #print(type(frame))
        #         p.stdin.write(frame.tostring())

            # if self.frame_queue1.empty() != True:
            #     frame = self.frame_queue1.get()
            #     # process frame
            #     # 你处理图片的代码
            #     # write to pipe
            #     #frame=get_img(frame)
                
            #     p.stdin.write(frame.tostring())
               

    def run(self):
        threads = [
            threading.Thread(target=Live.detection_push, args=(self,)),
            threading.Thread(target=Live.read_frame, args=(self,)),
            threading.Thread(target=Live.m_print, args=(self,)),
            threading.Thread(target=Live.push_frame, args=(self,))
        ]
        for thread in threads:
            thread.start()
live=Live()
live.run()