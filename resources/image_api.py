from flask import send_file, abort, request
from flask_restful import Resource
from werkzeug.utils import secure_filename
import os
import uuid
from google import genai
from PIL import Image, ImageOps  # 導入 Pillow
from google.genai import types  # 用於包裝圖片數據
from dotenv import load_dotenv

UPLOAD_FOLDER = os.path.join('static', 'avatars')

class ImageResource(Resource):
    def get(self):
        # 取得檔案的路徑
        img_path = os.path.join('static', 'avatars', 'cat1.jpg')

        if not os.path.exists(img_path):
            abort(404, description="圖片檔案不存在")

        # 回傳圖片檔案
        return send_file(img_path, mimetype='image/jpeg')
    
    def post(self):
        # 取得上傳的圖片，image 是formdata中的欄位名稱
        image = request.files.get('image')

        # 如果 image 不存在，或者 檔名是空的
        if not image or image.filename == '':
            abort(400, description="請選擇圖片檔案")

        original_filename = secure_filename(image.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'

        #檢查副檔名是基本功，檢查檔案內容才是真功夫。
        # 允許的副檔名集合
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        if ext not in ALLOWED_EXTENSIONS:
            abort(400, description="只能上傳圖片")

        # 產生全新的 UUID 檔名
        new_filename = f"{uuid.uuid4().hex}.{ext}"

        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        image.save(filepath)

        # ================ 使用 Gemini API 進行圖片處理 ================
        # load_dotenv()  # 讀取 .env 檔案
        # gemini_api_key = os.getenv('GEMINI_API_KEY')
        # client = genai.Client(api_key=gemini_api_key)


        # print("--- 你可以使用的模型清單 ---")
        # for model in client.models.list():
        #     print(f"模型名稱: {model.name}")

        # # 3. 【Pillow 核心處理】
        # # 使用 Pillow 打開圖片
        # img = Image.open(filepath)
            
        # # 自動校正圖片方向 (修正手機拍照可能橫倒的問題)
        # img = ImageOps.exif_transpose(img)
            
        # # 選用：壓縮圖片大小以節省 Token (限制最大邊為 1024px)
        # img.thumbnail((1024, 1024))
      
     

        # 1. 直接讀取圖片的二進位內容
        # image_data = image.read()
    
        # 2. 封裝成 Gemini 要求的格式
        # mime_type 必須根據檔案格式設定 (image/jpeg, image/png 等)
        # contents = [
        #     {
        #         "mime_type": image.content_type, 
        #         "data": image_data
        #     },
        #     "這是一隻貓還是狗？請告訴我品種。"
        # ]
    
        # 3. 呼叫 Gemini        
        # response = client.models.generate_content(
        #         model="models/gemini-2.0-flash",
        #         contents=[
        #             img,
        #             "這張圖片裡是貓還是狗？請告訴我品種，並簡短描述牠的樣子。"
        #         ]
        #     )



        # with open(filepath, "rb") as img_file:
        #     response = genai.images.generate_edit(
        #         model="gemini-1.5-image-edit-alpha",
        #         image=img_file,
        #         prompt="將圖片轉成卡通風格",
        #         n=1,
        #         size="512x512"
        #     )
        # edited_image_url = response['data'][0]['url']
        # # 下載並覆蓋原本的圖片
        # import requests
        # img_data = requests.get(edited_image_url).content   
        # with open(filepath, 'wb') as handler:
        #     handler.write(img_data)

        

        return {
            'message': '檔案上傳成功',
            # 'result': response.text,
            'url': f'{UPLOAD_FOLDER}\{new_filename}'
        }