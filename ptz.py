from onvif import ONVIFCamera
import zeep
import json
import cv2
import numpy as np
import sys
from PIL import Image
from time import sleep

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

def move(ip,port,account,pwd,pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed):
    mycam=ONVIFCamera(ip,port,account,pwd)
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

def movee(pan,pan_speed=1,tilt=0,tilt_speed=1,zoom=0,zoom_speed=1):
    mycam=ONVIFCamera('192.168.0.64',80,'admin','abc12345')
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]
    #print(media_profile)
    m_request = ptz.create_type('AbsoluteMove')
    m_request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})
    print(ptz.GetStatus({'ProfileToken': media_profile.token}))
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



def get_point():
    mycam=ONVIFCamera('192.168.0.64',80,'admin','abc12345')
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]
    #print(media_profile)
    jsonStr=ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    return jsonStr['PanTilt']['x'],jsonStr['PanTilt']['y'],jsonStr['Zoom']['x'],

def get_angle():
    x,y,z=get_point()
    angle_x=180*x-90
    print(x,y)
    angle_y=-45*y+45
    return angle_x,angle_y


def rad(x):
    return x * np.pi / 180
 
def get_warpR(img,anglex,angley,anglez):
    r=0
    w, h = img.shape[0:2]
    # 镜头与图像间的距离，21为半可视角，算z的距离是为了保证在此可视角度下恰好显示整幅图像
    z = np.sqrt(w ** 2 + h ** 2) / 2 / np.tan(rad(10))
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
    result = cv2.warpPerspective(img, warpR, img.shape[:2])
    return result

def paste(background,img):
    angleX,angleY=get_angle()
    print('============================'+str(angleX)+'============================'+str(angleY))
    warpR = get_warpR(img,angleY,0,angleX)
    image=Image.fromarray(np.uint8(warpR))
    r,g,b,a=image.split()
    background.paste(image,(0,  0, image.size[0], image.size[1]),a)
    
    return cv2.cvtColor(np.asarray(background), cv2.COLOR_RGB2BGR)

def continuous_move(direction,smooth,ip,port,account,password):
    smooth=float(smooth)
    mycam = ONVIFCamera(ip, port, account, password)
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile.token
    if(request.Velocity is None):
        request.Velocity=ptz.GetConfigurations()[0].DefaultPTZSpeed
    #request.Velocity.PanTilt.space=None
    #request.Velocity.Zoom.space=None
    ptz.Stop({'ProfileToken': media_profile.token})

    if(direction=='right'):
        request.Velocity.PanTilt.x = 1
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x=0
        request.Timeout=10000
        ptz.ContinuousMove(request)
        sleep(smooth)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='left'):
        request.Velocity.PanTilt.x = -1
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x=0
        request.Timeout=10000
        ptz.ContinuousMove(request)
        sleep(smooth)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='down'):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = -1
        request.Velocity.Zoom.x=0
        request.Timeout=10000
        ptz.ContinuousMove(request)
        sleep(smooth)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='up'):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 1
        request.Velocity.Zoom.x=0
        request.Timeout=10000
        ptz.ContinuousMove(request)
        sleep(smooth)
        ptz.Stop({'ProfileToken': request.ProfileToken})

def continue_movee(pan=0,pan_speed=1,tilt=0,tilt_speed=1,zoom=0,zoom_speed=1,ip='192.168.0.64',port=80,account='admin',password="abc12345"):
    mycam=ONVIFCamera(ip,port,account,password)
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]
    #print(media_profile)
    m_request = ptz.create_type('AbsoluteMove')
    m_request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})
    #print(ptz.GetStatus({'ProfileToken': media_profile.token}))

    if m_request.Position is None:
        m_request.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    if m_request.Speed is None:
        m_request.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position


    m_request.Position.PanTilt.x = m_request.Position.PanTilt.x+pan
    if( m_request.Position.PanTilt.x>1):
        m_request.Position.PanTilt.x-=2
    if( m_request.Position.PanTilt.x<-1):
        m_request.Position.PanTilt.x+=2
    m_request.Speed.PanTilt.x = pan_speed

    m_request.Position.PanTilt.y = m_request.Position.PanTilt.y+tilt
    if(m_request.Position.PanTilt.y>1):
        m_request.Position.PanTilt.y=1
    if(m_request.Position.PanTilt.y<-1):
        m_request.Position.PanTilt.y=-1
    m_request.Speed.PanTilt.y = tilt_speed

    m_request.Position.Zoom.x =m_request.Position.Zoom.x+zoom
    if(m_request.Position.Zoom.x>1):
        m_request.Position.Zoom.x=1
    if(m_request.Position.Zoom.x<-1):
        m_request.Position.Zoom.x=-1
    m_request.Speed.Zoom.x = zoom_speed

    #print(str(m_request.Position.PanTilt.x)+'============================================='+str(pan))
    #print(str(m_request.Position)+'============================================='+str(pan))
    
    ptz.AbsoluteMove(m_request)
    print(ptz.GetStatus({'ProfileToken': media_profile.token}))

def continue_move(direction,ip='192.168.0.64',port=80,account='admin',password="abc12345"):
    if(direction=='up'):
        continue_movee(tilt=-1/18,ip=ip,port=port,account=account,password=password)
    if(direction=='down'):
        continue_movee(tilt=1/18,ip=ip,port=port,account=account,password=password)
    if(direction=='left'):
        continue_movee(pan=1/36,ip=ip,port=port,account=account,password=password)
    
    if(direction=='right'):
        continue_movee(pan=-1/36,ip=ip,port=port,account=account,password=password)
        