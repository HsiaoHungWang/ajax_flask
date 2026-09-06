"""景點圖片辨識 —— 地端模型版（Ollama + SSE 串流）

與雲端 SSE 版（attraction_recognition_stream_api.py）唯一的差別：
模型從 Google Gemini（雲端 API）換成本機 Ollama 跑的視覺模型。
傳輸方式完全一樣（SSE / text/event-stream / 打字機），
用來對照「同一套傳輸，模型放雲端 vs 放地端」的取捨。

前置需求：
  1. 安裝 Ollama 並讓它在背景執行（預設 http://localhost:11434）
  2. 先下載一個「看得懂圖」的視覺模型，例如：
         ollama pull qwen2.5vl:3b

可用環境變數覆蓋預設值：
  OLLAMA_HOST   （預設 http://localhost:11434）
  OLLAMA_MODEL  （預設 qwen2.5vl:3b）
"""

import base64
import json
import mimetypes
import os

import requests
from flask import Response, request, stream_with_context


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8MB

# 小模型容易陷入「一直重複同一句」的退化迴圈，這裡再加一道伺服器端硬上限：
# 正常情況由 num_predict 收尾（約 200～300 字），這個上限只在真的鬼打牆時才觸發。
MAX_OUTPUT_CHARS = 400

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5vl:3b")

# 交給 Ollama 的生成參數：限制長度 + 加重重複懲罰，壓制小模型的鬼打牆
OLLAMA_OPTIONS = {
    "num_predict": 260,        # 約 200 中文字所需的 token 數 + 緩衝
    "repeat_penalty": 1.4,     # 預設 1.1，調高讓它不要一直重複同一句
    "repeat_last_n": 128,
    "temperature": 0.6,        # 太低反而容易貪婪解碼卡住重複，給一點隨機性
}

# 小模型多半不認得特定景點，硬要它寫「歷史／遊玩方式」只會逼它胡謅。
# 改成單純「描述你看到的畫面」，這是小型視覺模型做得到的事。
PROMPT = (
    "請用繁體中文描述這張照片的內容，大約 200 個字，寫成一段通順的文字。"
    "只描述畫面上實際看得到的東西（地形、建築、人物、天氣、氛圍等），"
    "不要臆測地名或歷史，不要寫客套話，不要用條列或 Markdown。"
)


def _sse(payload: dict) -> str:
    """把 dict 包成一個 SSE 事件字串：`data: {...}\\n\\n`"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def attraction_recognize_local():
    # ---- 1. 串流開始前的檢查，用正常 HTTP 狀態碼 ----
    image = request.files.get("image")
    if image is None or image.filename == "":
        return {"error": "請選擇景點圖片"}, 400

    mime_type = image.mimetype or mimetypes.guess_type(image.filename)[0]
    if mime_type not in ALLOWED_MIME_TYPES:
        return {"error": "只支援 JPG、PNG、WEBP、HEIC 或 HEIF 圖片"}, 400

    image_bytes = image.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return {"error": "圖片檔案過大（上限 8MB）"}, 400

    # Ollama 的圖片是用 base64 字串帶進 JSON（不是 multipart）
    image_b64 = base64.b64encode(image_bytes).decode()

    # ---- 2. 產生器：把 Ollama 的 NDJSON 串流轉成 SSE ----
    @stream_with_context
    def event_stream():
        try:
            with requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": PROMPT,
                    "images": [image_b64],
                    "stream": True,
                    "options": OLLAMA_OPTIONS,
                },
                stream=True,
                timeout=(5, 300),   # 連線 5 秒逾時、讀取最長 300 秒
            ) as resp:
                if resp.status_code == 404:
                    yield _sse({
                        "error": f"Ollama 找不到模型「{OLLAMA_MODEL}」，"
                                 f"請先執行：ollama pull {OLLAMA_MODEL}"
                    })
                    return
                resp.raise_for_status()

                # Ollama 串流：一行一個 JSON，response 是一小段文字、done 為結束旗標
                total_chars = 0
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if chunk.get("error"):
                        yield _sse({"error": f"Ollama 錯誤：{chunk['error']}"})
                        return
                    text = chunk.get("response", "")
                    if text:
                        yield _sse({"delta": text})
                        total_chars += len(text)
                    if chunk.get("done"):
                        break
                    # 硬上限：小模型鬼打牆時直接切斷（關閉連線會一併停止 Ollama 生成）
                    if total_chars >= MAX_OUTPUT_CHARS:
                        yield _sse({"delta": "…（內容過長，已截斷）"})
                        break

            yield _sse({"done": True})

        except requests.exceptions.ConnectionError:
            yield _sse({"error": f"連不上 Ollama（{OLLAMA_URL}），請確認 Ollama 已啟動"})
        except Exception as error:
            yield _sse({"error": f"景點辨識失敗：{error}"})

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
