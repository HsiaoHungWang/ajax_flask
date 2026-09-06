from flask import Blueprint, render_template

page_bp = Blueprint('page', __name__)

@page_bp.route('/')
def index():
    return render_template('index.html')

@page_bp.route('/json')
def json():
    return render_template('json.html')

@page_bp.route('/response_body')
def image():
    return render_template('response_body.html')

@page_bp.route('/address')
def address():
    return render_template('address.html')

@page_bp.route('/members')
def members():
    return render_template('members.html')

@page_bp.route('/request_data')
def demo():
    return render_template('request_data.html')

@page_bp.route('/attraction')
def attraction():
    return render_template('attraction.html')

@page_bp.route('/recognize')
def recognize():
    return render_template('recognize.html')

@page_bp.route('/recognize-stream')
def recognize_stream():
    return render_template('recognize_stream.html')

@page_bp.route('/recognize-local')
def recognize_local():
    return render_template('recognize_local.html')

@page_bp.route('/clock')
def clock():
    return render_template('clock.html')

@page_bp.route('/ws-hello')
def ws_hello():
    return render_template('ws_hello.html')

@page_bp.route('/recognize-ws')
def recognize_ws():
    return render_template('recognize_ws.html')

@page_bp.route('/barchart')
def barchart():
    return render_template('barchart.html')

@page_bp.route('/map')
def map():
    return render_template('map.html')


