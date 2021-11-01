from flask import Flask,request,render_template
import json
app = Flask(__name__)

@app.route('/',methods=["POST","GET"])
def index():
    return 'Hello_Teammates'

if __name__ == "__main__":
    app.run(port=9000)