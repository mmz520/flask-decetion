import cv2
from flask import Flask,render_template,Response,request,make_response
from flask_caching import Cache
from video_camera import VideoCamera
from m_threading import MyThread
from ptz import move,movee,continue_movee,continuous_move
from get_ptz_ref import get_ptz,get_ptz_xyz
import json
from flask_cors import *

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask('server1')
# tell Flask to use the above defined config
app.config.from_mapping(config)
CORS(app=app,supports_credentials=True)
cache = Cache(app)

t=None


def gen(camera):
    print('传输开始')
    while True:
        #print('传输进行中...')
        frame = camera.get_frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed/<enable_detect>/<way>/<index>')  # 这个地址返回视频流响应
def video_feed(enable_detect,way,index):
    #print('线程开启')
    t=MyThread(gen,(VideoCamera(enable_detect,way,index),),gen.__name__)
    t.start()
        
    return Response(t.get_result(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')   
    #  return Response(gen(VideoCamera(enable_detect,way,index)),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')   


@app.route('/ptz/<ip>/<port>/<account>/<pwd>/<pan>/<pan_speed>/<tilt>/<tilt_speed>/<zoom>/<zoom_speed>')
def ptz(ip,port,account,pwd,pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed):
    move(ip,port,account,pwd,pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed)
    return 'ptz: success'

@app.route('/ptz/<pan>/<pan_speed>/<tilt>/<tilt_speed>/<zoom>/<zoom_speed>')
def ptzzz(pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed):
    movee(pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed)
    return 'ptz: success'

@app.route('/ptzz/<camera_x>/<camera_y>/<oringin_x>/<origin_y>/<target_x>/<target_y>',methods=['POST'])
def ptzzzz(camera_x,camera_y,oringin_x,origin_y,target_x,target_y):
    data=request.get_data()
    json_data=json.loads(data)
    ip=json_data.get('ip')
    port=json_data.get('port')
    account=json_data.get('account')
    password=json_data.get('password')
    continue_movee( pan=get_ptz_xyz(camera_x,camera_y,oringin_x,origin_y,target_x,target_y),ip=ip,port=port,account=account,password=password)
    response = make_response('ptz: success')
    response.headers['Access-Control-Allow-Origin'] = '*'
    # return jsonify(data)
    return response     

@app.route('/ptzmove/<direction>/<smooth>',methods=['POST'])
def ptzmove(direction,smooth):
    data=request.get_data()
    json_data=json.loads(data)
    ip=json_data.get('ip')
    port=json_data.get('port')
    account=json_data.get('account')
    password=json_data.get('password')
    continuous_move(direction,smooth,ip=ip,port=port,account=account,password=password)
    return 'ptz: success'

# @app.route('/ptz')
# def ptzzzzz():
#     continue_movee( pan=get_ptz('(0,0)','(1,1)','(1,0)'))
#     return 'ptz: success'

@app.route('/')
def test1():
    return render_template('index.html')


@app.route('/h5')
def test2():
    return render_template('indexH5.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)