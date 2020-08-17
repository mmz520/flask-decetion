import darknet
from deal_derection import deal_object
import cv2
import os
from draw_box import Chinese_plot_box,myThread
from target import Target
#from deal_derection import deal_object
from PIL import Image, ImageDraw, ImageFont
import numpy as np

netMain = None
metaMain = None
altNames = None

last=[]

configPath = "./cfg/yolov4.cfg"
weightPath = "./yolov4.weights"
metaPath = "./cfg/coco.data"

netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)
metaMain = darknet.load_meta(metaPath.encode("ascii"))

darknet_image = darknet.make_image(darknet.network_width(netMain),
    darknet.network_height(netMain),3)


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype('NotoSerifCJK-Bold.ttc', textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def list_contain_name(lists,name):
    for index in range(len(lists)):
        if(lists[index].name==name):
            return index
    return  -1


def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def cvDrawBoxes(detections, img,left=0,top=0,textColor=(0, 255, 0),textSize=15):
    list_find=[]
    for index in range(len(detections)) :
        name=detections[index][0].decode()
        m_target=Target(name)
        m_index=list_contain_name(list_find,name)
        if m_index==-1:
            list_find.append(m_target)
        else:
            list_find[m_index].count+=1
        x, y, w, h = detections[index][2][0],\
            detections[index][2][1],\
            detections[index][2][2],\
            detections[index][2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        label=detections[index][0].decode()+'['+str(round(detections[index][1]*100,2))+']'
        #print(label)
        img=Chinese_plot_box(img,label,[xmin,ymin,xmax,ymax],12,line_color=None,line_thickness=1)       
        find_object=detections[index][0].decode()
    

    for index in range(len(list_find)) :
        text=list_find[index].name+":"+str(list_find[index].count) 
        img=cv2ImgAddText(img, text, left, top+textSize*index, textColor, textSize)
    img=cv2.resize(img,(640,480))
    deal_object(list_find,img)

    return img

def get_img(frame_read):
    frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb,
                                (darknet.network_width(netMain),
                                darknet.network_height(netMain)),
                                interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
    detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
    image = cvDrawBoxes(detections, frame_resized,500,10,(255,0,51),15)
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
