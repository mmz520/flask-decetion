import subprocess as sp
import cv2 
import ffmpeg
from get_derection import get_img

rtmpUrl = "rtmp://192.168.0.236:1935/live/test4"
camera_path = "rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101"
cap = cv2.VideoCapture(camera_path)

# Get video information
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ffmpeg command
command = ['ffmpeg',
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
        rtmpUrl]
#command=['ffmpeg -re -i rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101 -vcodec copy -acodec copy -f flv rtmp://127.0.0.1:1935/live/test1']

# 管道配置
p = sp.Popen(command, stdin=sp.PIPE)

# read webcamera
while(cap.isOpened()):
    ret, frame = cap.read()
    #cv2.putText(frame,"aha")
    if not ret:
        print("Opening camera is failed")
        break
    frame=get_img(frame)
    p.stdin.write(frame.tostring())