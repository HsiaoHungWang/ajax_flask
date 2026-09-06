"""景點圖片辨識 —— SSE 串流版（打字機效果）

與 attraction_recognition_api.py 的差異：
  - 舊版：client.models.generate_content(...)  一次算完、一次回整包 JSON
  - 本版：client.models.generate_content_stream(...)  邊算邊吐，
          透過 SSE（text/event-stream）把一段一段文字即時推給瀏覽器，
          前端收到就顯示，形成類似 ChatGPT 的打字機效果。

注意：串流不適合用 flask_restful 的 Resource（它會把回傳值序列化成 JSON），
所以這裡寫成一般的 Flask view function，由 routes/api.py 用 add_url_rule 掛上路由。
"""

import json
import mimetypes
import os

from flask import Response, request, stream_with_context
from google import genai


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

# 串流版改用「自然語言」輸出，最能展示打字機效果；
# 不使用 response_schema，因為 JSON 在串流過程中是半截的、無法逐段解析。
PROMPT = (
    "你是一位熟悉世界各地的旅遊導覽員。請辨識這張照片中的景點，"
    "用繁體中文寫一段 150～250 字的介紹，內容包含：景點名稱、所在的國家與縣市／鄉鎮、"
    "歷史或特色、以及適合的遊玩方式。請寫成通順的段落，"
    "不要用條列、不要用 Markdown 標題或星號。若無法確定景點，請直接說明無法辨識。"
)


def _sse(payload: dict) -> str:
    """把 dict 包成一個 SSE 事件字串：`data: {...}\\n\\n`"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def attraction_recognize_stream():
    # ---- 1. 先做一般的參數檢查，這些錯誤發生在串流開始前，可以用正常 HTTP 狀態碼回 ----
    image = request.files.get("image")
    if image is None or image.filename == "":
        return {"error": "請選擇景點圖片"}, 400

    mime_type = image.mimetype or mimetypes.guess_type(image.filename)[0]
    if mime_type not in ALLOWED_MIME_TYPES:
        return {"error": "只支援 JPG、PNG、WEBP、HEIC 或 HEIF 圖片"}, 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "伺服器尚未設定 GEMINI_API_KEY"}, 500

    # 先把檔案讀成 bytes；因為 generator 執行時，request 內容可能已被回收
    image_bytes = image.read()

    # ---- 2. 產生器：每 yield 一次，就往瀏覽器推一個 SSE 事件 ----
    @stream_with_context
    def event_stream():
        try:
            client = genai.Client(api_key=api_key)
            image_part = genai.types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )
            stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=[image_part, PROMPT],
            )
            for chunk in stream:
                # 每個 chunk 可能一次帶好幾個字；前端再自己逐字慢慢吐
                if chunk.text:
                    yield _sse({"delta": chunk.text})
            # 用一個結束哨兵告訴前端「串流正常結束」
            yield _sse({"done": True})
        except Exception as error:
            # 串流一旦開始，HTTP 狀態碼已經是 200，錯誤只能「寫在資料流裡」傳給前端
            yield _sse({"error": f"景點辨識失敗：{error}"})

    # ---- 3. 回傳串流 Response ----
    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",   # 不要快取串流內容
            "X-Accel-Buffering": "no",     # 提示 nginx 等反向代理不要緩衝，立即轉發
        },
    )
