import json
import mimetypes
import os

from flask import request
from flask_restful import Resource
from google import genai


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "AttractionName": {"type": "STRING"},
        "Country": {"type": "STRING"},
        "City": {"type": "STRING"},
        "Town": {"type": "STRING"},
        "Description": {"type": "STRING"},
        "Latitude": {"type": "STRING"},
        "Longitude": {"type": "STRING"},
    },
    "required": [
        "AttractionName",
        "Country",
        "City",
        "Town",
        "Description",
        "Latitude",
        "Longitude",
    ],
}


class AttractionImageRecognition(Resource):
    def post(self):
        image = request.files.get("image")
        if image is None or image.filename == "":
            return {"error": "請選擇景點圖片"}, 400

        mime_type = image.mimetype or mimetypes.guess_type(image.filename)[0]
        if mime_type not in ALLOWED_MIME_TYPES:
            return {"error": "只支援 JPG、PNG、WEBP、HEIC 或 HEIF 圖片"}, 400

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "伺服器尚未設定 GEMINI_API_KEY"}, 500

        try:
            client = genai.Client(api_key=api_key)
            image_part = genai.types.Part.from_bytes(
                data=image.read(),
                mime_type=mime_type,
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image_part,
                    (
                        "請辨識這張照片中的景點，只回傳符合指定欄位的 JSON。"
                        "無法確認的欄位請填空字串，所有欄位都必須是字串，使用繁體中文回應。"
                    ),
                ],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            result = json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Gemini 回傳的內容不是有效 JSON"}, 502
        except Exception as error:
            return {"error": f"景點辨識失敗：{error}"}, 502

        return result, 200
