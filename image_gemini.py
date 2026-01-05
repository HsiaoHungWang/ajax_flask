import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def describe_image_with_gemini(image_path):
    # 1. 開啟圖片
    img = Image.open(image_path)

    prompt = """
        請分析這張圖片，並嚴格以 JSON 格式回傳以下內容：
        1. "main": 一句話總結這張圖片的主題。
        2. "tags": 提取 3-5 個與圖片相關的繁體中文標籤（陣列格式）。
        3. "description": 詳細描述圖片細節，包含構圖、顏色與主體特徵（使用繁體中文）。
    
        請確保輸出是純粹的 JSON 格式。
    """
    
    # 呼叫 Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt, # "請詳細描述這張圖片的內容，並用繁體中文回答。",
            img
        ]
    )
    return response.text

# 測試
print(describe_image_with_gemini('static/avatars/dog3.jpg'))

