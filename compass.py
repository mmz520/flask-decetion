import cv2
import numpy as np
import sys

def rotate (img, angle):
    rows,cols ,count= img.shape[:2]
    # cols-1 and rows-1 are the coordinate limits.
    M = cv2.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),-angle,1)
    dst = cv2.warpAffine(img,M,(cols,rows))
    return dst

def perspective(img,angle):
    h,w=img.shape[:2]
    pts=np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]])
    cv2.circle(img,(0,h-1),36,(0,290,0),-1)
    pts1 = np.float32([ [0,0],[200,h-36],[w-36,h-36],[w-1,0] ])
    M = cv2.getPerspectiveTransform(pts,pts1)
    dst = cv2.warpPerspective(img,M,(500,526))
    return dst



def rad(x):
    return x * np.pi / 180
 
def get_warpR(img,anglex,angley,anglez,fov=42,r=0):
    w, h = img.shape[:2]
    # 镜头与图像间的距离，21为半可视角，算z的距离是为了保证在此可视角度下恰好显示整幅图像
    z = np.sqrt(w ** 2 + h ** 2) / 2 / np.tan(rad(fov / 2))
    # 齐次变换矩阵
    rx = np.array([[1, 0, 0, 0],
                   [0, np.cos(rad(anglex)), -np.sin(rad(anglex)), 0],
                   [0, -np.sin(rad(anglex)), np.cos(rad(anglex)), 0, ],
                   [0, 0, 0, 1]], np.float32)
 
    ry = np.array([[np.cos(rad(angley)), 0, np.sin(rad(angley)), 0],
                   [0, 1, 0, 0],
                   [-np.sin(rad(angley)), 0, np.cos(rad(angley)), 0, ],
                   [0, 0, 0, 1]], np.float32)
 
    rz = np.array([[np.cos(rad(anglez)), np.sin(rad(anglez)), 0, 0],
                   [-np.sin(rad(anglez)), np.cos(rad(anglez)), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]], np.float32)
 
    r = rx.dot(ry).dot(rz)
 
    # 四对点的生成
    pcenter = np.array([h / 2, w / 2, 0, 0], np.float32)
 
    p1 = np.array([0, 0, 0, 0], np.float32) - pcenter
    p2 = np.array([w, 0, 0, 0], np.float32) - pcenter
    p3 = np.array([0, h, 0, 0], np.float32) - pcenter
    p4 = np.array([w, h, 0, 0], np.float32) - pcenter
 
    dst1 = r.dot(p1)
    dst2 = r.dot(p2)
    dst3 = r.dot(p3)
    dst4 = r.dot(p4)
 
    list_dst = [dst1, dst2, dst3, dst4]
 
    org = np.array([[0, 0],
                    [w, 0],
                    [0, h],
                    [w, h]], np.float32)
 
    dst = np.zeros((4, 2), np.float32)
 
    # 投影至成像平面
    for i in range(4):
        dst[i, 0] = list_dst[i][0] * z / (z - list_dst[i][2]) + pcenter[0]
        dst[i, 1] = list_dst[i][1] * z / (z - list_dst[i][2]) + pcenter[1]
 
    warpR = cv2.getPerspectiveTransform(org, dst)
    return warpR
 


img=cv2.imread("test.png",cv2.IMREAD_UNCHANGED)
cv2.imwrite("out.png",get_warpR(img,0,0,0))

