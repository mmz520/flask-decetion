import ffmpeg
import socket
from flask import Flask,Response,render_template



packet_size = 4096

app=Flask(__name__)

@app.route('/')
def test():
    def gen():       
        process = (
            ffmpeg
            .input('rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/501')
            .output('out.flv')
            #.output('pipe:', format='h264')
            #.output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
        while True:
            out, err = process.communicate()
            print(str(out))
            yield out
    
    response=Response(gen(),200)
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Type', 'application/octet-stream')
    #response.headers.add('Content-Range', 'bytes {}-{}/{}'.format(sk, end, total))
    return response


@app.route('/h5')
def index():
    return render_template('indexH5.html')
app.run()






