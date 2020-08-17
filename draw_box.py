# -*- coding:utf-8 _*-
"""
@Author:Linda Li
@Time:2020/7/23 下午9:25
"""
# coding=utf-8
# cv2解决绘制中文乱码

import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont
import os
import threading
#区别就是local是左上角的值，但是x是左上角和右下角的值


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype('NotoSerifCJK-Bold.ttc', textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


class myThread (threading.Thread):
    result=None
    def __init__(self, image,label,x,sizes,colour=None,line_thickness=None):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        self.image=image
        self.label=label
        self.x=x
        self.sizes=sizes
        self.colour=colour
        self.line_thickness=line_thickness
    def run(self):
        print ("开始线程：" + self.name)
        self.result= Chinese_plot_box(self.image,self.label,self.x,self.sizes,self.colour,self.line_thickness)
        print ("退出线程：" + self.name)
    def result(self):
        return self.result


def Chinese_plot_box(image,label,x,sizes,line_color=None,line_thickness=None):
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    cv2img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pilimg = Image.fromarray(cv2img)
    draw = ImageDraw.Draw(pilimg)  
    font = ImageFont.truetype("NotoSerifCJK-Bold.ttc",sizes, encoding="utf-8")
    
    tl = line_thickness or round(0.001 * (image.shape[0] + image.shape[1]) / 2) 
    draw.rectangle([int(x[0]), int(x[1]), int(x[2]), int(x[3])], outline=(255, 0, 0),
                fill=None, width=tl)
    if label:
        tf = max(tl - 1, 1)  # font thickness  字体大小
        t_size_x=get_len(label,sizes)
        draw.rectangle([int(x[0]),int(x[1]),int(x[0]) + t_size_x,int(x[1])  -sizes-5], outline=(255,0,0),fill=(255,0,0),width=1)

        draw.text(((int(x[0]), int(x[1])-sizes-5)), label, (255,255,255), font=font)
        image = cv2.cvtColor(numpy.array(pilimg), cv2.COLOR_RGB2BGR)
    return image

def get_len(label,sizes):
    num='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    strs=label.split('[')
    count_1=0
    have=False
    for c in strs[0]:
        if(num.__contains__(c)):
            count_1+=0.5     
            have=True     
        else:
            count_1+=1
    if  have:
        count_1+=0.5

    count=count_1+(len(strs[1])+1)/2
    return count*sizes

if __name__ == '__main__':
    im0 = cv2.imread('timg.jpeg')
    img = Chinese_plot_box(im0, label='动物[24.5444444]', x=[523,719,641,823], sizes=10, colour=None, line_thickness=None)
    #cv2.imshow('show', img)
    cv2.imwrite('timg1.jpeg', img)