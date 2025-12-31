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

@page_bp.route('/spots')
def spot():
    return render_template('spots.html')

@page_bp.route('/barchart')
def barchart():
    return render_template('barchart.html')

@page_bp.route('/map')
def map():
    return render_template('map.html')

# http://127.0.0.1:5000/user
@page_bp.route('/user')
def user():
    return render_template('user.html')


