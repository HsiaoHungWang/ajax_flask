from flask import request
from flask_restful import Resource

class QueryStringDemo(Resource):
    def get(self):
        # 使用 request.args 取得資料
        name = request.args.get('name', '預設值')
        age = request.args.get('age')
        return {"method": "QueryString", "name": name, "age": age}, 200

class PathDemo(Resource):
    def get(self, name, age): # 變數會直接作為參數傳入
        return {"method": "PathParameter", "name": name, "age": age}, 200
    
class FormDataDemo(Resource):
    def post(self):
        # 接收一般文字欄位
        name = request.form.get('name')
        age = request.form.get('age')
        
        # 如果有上傳檔案，使用 request.files
        # file = request.files.get('photo')
        
        return {"method": "FormData", "received": {"name": name, "age": age}}, 201

class JsonDemo(Resource):
    def post(self):
        # 取得 JSON 內容，若前端沒傳會回傳 None
        data = request.get_json()
        
        name = data.get('name')
        age = data.get('age')
        
        return {"method": "JSON", "received": data}, 201