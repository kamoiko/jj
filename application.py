from flask import Flask
from flask import request
import flask

app = Flask(__name__)
@app.route('/')
def index():
    return "HI"
