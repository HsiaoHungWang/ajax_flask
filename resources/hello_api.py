from flask_restful import Resource
from flask import make_response, send_file, abort
import time, os
class HelloWorld(Resource):
    def get(self):
        time.sleep(5)  # 模擬延遲
        return {'message':'Hello, RESTful API!!'},200
    
class TextResource(Resource):
    def get(self):
        response = make_response("RESTful API", 200)
        response.mimetype = "text/plain"
        return response
        # return "RESTful API"
    
class ImageResource(Resource):
    def get(self):
        # 取得檔案的路徑
        img_path = os.path.join('static', 'avatars', 'cat1.jpg')

        if not os.path.exists(img_path):
            abort(404, message="圖片檔案不存在")

        # 回傳圖片檔案
        return send_file(img_path, mimetype='image/jpeg')


class JsonResource(Resource):
    def get(self):
        # Python List 包含多個 Dictionary
        todo_list = [
            {
                "id": 1,
                "task": "學習 Flask-RESTful",
                "completed": True
            },
            {
                "id": 2,
                "task": "撰寫 AJAX fetch 練習",
                "completed": False
            },
            {
                "id": 3,
                "task": "實作圖片上傳功能",
                "completed": False
            }
        ]

        # 直接回傳資料與狀態碼 200
        # flask-restful 會自動執行 jsonify(todo_list)
        return todo_list, 200
    



     
