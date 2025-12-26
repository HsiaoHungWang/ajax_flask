from flask import Flask, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from routes.page import page_bp
from routes.api import api_bp
from models import db # 從 models/__init__.py 匯入 db 物件
import os

# 建立 Flask 物件
app = Flask(__name__)

# 對 app 套用 CORS
CORS(app)


#將 Flask 應用程式轉成 RESTful API 的架構
api = Api(app)  



# 設定資料庫
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydb.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化
db.init_app(app)

#測試讀取.env 檔案
# import os
# from dotenv import load_dotenv
# load_dotenv()  # 讀取 .env 檔案
# gemini_api_key = os.getenv('GEMINI_API_KEY')
# print("GEMINI_API_KEY =", gemini_api_key)

#Demo1
# @app.route('/home')
# def home():
#     return "Hello, World!"

#Demo2
# @app.route('/')
# def index():
#     return render_template('index.html') 

#Demo3
# class HelloWorld(Resource):       # HelloWorld Class 就是一個 API
#     def get(self):
#         return {'message': 'Hello, RESTful API!'} 

# api.add_resource(HelloWorld, '/')              

# 好一點的架構
# 註冊 Blueprint
app.register_blueprint(page_bp)
app.register_blueprint(api_bp, url_prefix='/api')
# app.register_blueprint(api_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
