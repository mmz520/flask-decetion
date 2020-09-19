import queue
import threading
import cv2 as cv
import subprocess as sp
from get_derection import get_img
import numpy as np
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
        self.command = ""
        # 自行设置
        self.rtmpUrl = "rtmp://192.168.0.236:1935/live/camera2"
        self.camera_path = "rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101"
        #self.camera_path = "rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101"
        self.cap = cv.VideoCapture(self.camera_path)

    def detection(self):
        cap = cv.VideoCapture(self.camera_path)

        # read webcamera
        while(cap.isOpened()):
            ret, frame = cap.read()
            ret, frame = cap.read()
            ret, frame = cap.read()
            if not ret:
                print("Opening camera is failed")
                break
            frame=get_img(frame)
            # put frame into queue
            #darknet.copy_image_from_bytes(darknet_image,frame.tobytes())
            #detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
            self.frame_queue2.put(frame)

    def read_frame(self):
        cap = cv.VideoCapture(self.camera_path)
        print("开启推流")
        # Get video information
        fps = int(cap.get(cv.CAP_PROP_FPS))
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

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

        # read webcamera
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                print("Opening camera is failed")
                break
            
            # put frame into queue
            #darknet.copy_image_from_bytes(darknet_image,frame.tobytes())
            #detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
            self.frame_queue1.put(frame)

    def push_frame(self):
        # 防止多线程时 command 未被设置
        while True:
            if len(self.command) > 0:
                # 管道配置
                p = sp.Popen(self.command, stdin=sp.PIPE)
                break
        width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        laster=np.zeros((height,width,3),np.uint8)
        while True:    
            if not self.frame_queue2.empty() and not self.frame_queue1.empty():
                #print(self.frame_queue2.get().shape)
                laster=self.frame_queue2.get()
                frame=cv.add(laster,self.frame_queue1.get())
                #print(self.frame_queue2.get().shape)
                p.stdin.write(frame.tostring())
            elif not self.frame_queue1.empty():
                frame=cv.add(laster,self.frame_queue1.get())
                    
                #print(type(frame))
                p.stdin.write(frame.tostring())

            # if self.frame_queue1.empty() != True:
            #     frame = self.frame_queue1.get()
            #     # process frame
            #     # 你处理图片的代码
            #     # write to pipe
            #     #frame=get_img(frame)
                
            #     p.stdin.write(frame.tostring())
               

    def run(self):
        threads = [
            threading.Thread(target=Live.detection, args=(self,)),
            threading.Thread(target=Live.read_frame, args=(self,)),
            threading.Thread(target=Live.push_frame, args=(self,))
        ]
        for thread in threads:
            thread.start()
live=Live()
live.run()