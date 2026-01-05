from flask import request, abort
from flask_restful import Resource
import os, uuid
from werkzeug.utils import secure_filename
from PIL import Image
import models_loader
from dotenv import load_dotenv
from google import genai

load_dotenv() # 載入 .env 
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# http://127.0.0.1:5000/api/demo/query?name=Tom&age=27
class QueryStringDemo(Resource):
    def get(self):
        # 使用 request.args 取得 QueryString 資料
        name = request.args.get('name', '預設值')
        age = request.args.get('age')
        return {"method": "QueryString", "name": name, "age": age}, 200
    
# http://127.0.0.1:5000/api/demo/path/John/25
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

         #情緒分析
        feedback = data.get('feedback')
        result = models_loader.classifier(feedback)[0]

        #結合Genmini給建議
        prompt =  f"""
            學生的評論是{feedback}
            AI判定情緒是{result['label']}，信心度{result['score']}
            請以教學顧問的身分給50個字內的教學改善建議
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(response.text)
        
        return {
            "method": "JSON", 
            "received": data,
            "sentiment": result['label'],
            "score": f"{round(result['score'],4):.1%}",
            "suggestion":response.text
            }, 201
    
UPLOAD_FOLDER = os.path.join('static', 'uploads')

class ImageUploadDemo(Resource):
    def get(self):
        pass
    
    def post(self):
        # 取得上傳的圖片，image 是formdata中的欄位名稱
        image = request.files.get('image')

        # 如果 image 不存在，或者 檔名是空的
        if not image or image.filename == '':
            abort(400, description="請選擇圖片檔案")

        original_filename = secure_filename(image.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'

        # 允許的副檔名集合
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if ext not in ALLOWED_EXTENSIONS:
            abort(400, description="只能上傳圖片")

        # 產生全新的 UUID 檔名
        new_filename = f"{uuid.uuid4().hex}.{ext}"

        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        image.save(filepath)

        #影像描述
        # 讀取圖片
        raw_image = Image.open(filepath).convert('RGB')
         # 處理圖片
        inputs = models_loader.processor(raw_image, return_tensors="pt")
         # 生成文字
        out = models_loader.model.generate(**inputs, max_new_tokens=50)
        # 解碼輸出
        description = models_loader.processor.decode(out[0], skip_special_tokens=True)


        return {
            'message': '檔案上傳成功',
            'url': filepath,
            'description' : description
        }