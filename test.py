from flask import Flask,redirect


app=Flask(__name__)


@app.route('/')
def test():
    return redirect('https://www.baidu.com')

app.run()
