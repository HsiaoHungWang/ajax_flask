from flask import Blueprint, render_template

page_bp = Blueprint('page', __name__)

@page_bp.route('/')
def index():
    return render_template('index.html')

@page_bp.route('/image')
def image():
    return render_template('image.html')

@page_bp.route('/address')
def address():
    return render_template('address.html')

@page_bp.route('/members')
def members():
    return render_template('members.html')

@page_bp.route('/demo')
def demo():
    return render_template('demo.html') 