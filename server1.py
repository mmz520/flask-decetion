import cv2
from flask import Flask,render_template,Response,request
from flask_caching import Cache
from video_camera import VideoCamera
from m_threading import MyThread
from ptz import move


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask('server1')
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

t=None


def gen(camera):
    print('传输开始')
    while True:
        print('传输进行中...')
        frame = camera.get_frame()
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed/<enable_detect>/<way>/<index>')  # 这个地址返回视频流响应
def video_feed(enable_detect,way,index):
    print('线程开启')
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

@app.route('/')
def test1():
    return render_template('index.html')


@app.route('/h5')
def test2():
    return render_template('indexH5.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)