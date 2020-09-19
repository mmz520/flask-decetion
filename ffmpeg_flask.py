import ffmpeg
import socket
from flask import Flask,Response,render_template

process = (
            ffmpeg
            .input('rtsp://admin:abc12345@192.168.0.5:554/Streaming/Channels/101')
            #.output('')
            #.output('pipe:', format='h264')
            .output('rtmp://127.0.0.1:1935/live/test', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )






