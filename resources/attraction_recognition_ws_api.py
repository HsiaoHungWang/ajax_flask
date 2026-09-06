"""景點圖片辨識 —— WebSocket 版（含「停止生成」按鈕）

與 SSE 版（attraction_recognition_stream_api.py）的關鍵差異：
  - SSE 是「單向」：伺服器只能往瀏覽器推，client 對同一條連線沒有上行能力。
  - WebSocket 是「雙向 full-duplex」：同一條連線裡，
    伺服器一邊串流辨識結果，client 可以隨時送 {"type":"cancel"} 叫它停。
    這就是 SSE 在單一連線上做不到、非得用 WebSocket 的地方。

傳輸設計：
  1. client 先送一個「文字 frame」= 中繼資料 {"type":"image_meta", filename, mime, size}
  2. client 再送一個「二進位 frame」= 圖片位元組本身
     （WebSocket 沒有 multipart/form-data，要自己這樣拆）
  3. 伺服器驗證後，逐段送 {"type":"delta","text":...}
  4. 收尾送 {"type":"done"} 或 {"type":"stopped"} 或 {"type":"error"}

為什麼要開一條 worker 執行緒跑 Gemini？
  `for chunk in stream` 會「卡住」等 Gemini 回傳下一段（尤其是等第一個 token，
  這段期間畫面上一個字都還沒有）。卡住的時候，同一條執行緒就沒辦法同時去聽
  前端有沒有送「停止」。所以：
    - worker 執行緒：專心把 Gemini 的內容一段段送出去
    - 主執行緒：專心聽前端訊息，收到 cancel 立刻回 {"type":"stopped"} 並結束
  「一邊送、一邊收」要並行 —— 這就是全雙工在伺服器端的體現。

本檔不是 flask_restful 的 Resource，也不是一般 Flask view，
而是用 flask_sock 的 sock.route 掛在 api 藍圖上（見 routes/api.py 的 init_ws 呼叫）。
"""

import json
import mimetypes
import os
import threading

from google import genai


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8MB，buffer 圖片前先擋大小

PROMPT = (
    "你是一位熟悉世界各地的旅遊導覽員。請辨識這張照片中的景點，"
    "用繁體中文寫一段 150～250 字的介紹，內容包含：景點名稱、所在的國家與縣市／鄉鎮、"
    "歷史或特色、以及適合的遊玩方式。請寫成通順的段落，"
    "不要用條列、不要用 Markdown 標題或星號。若無法確定景點，請直接說明無法辨識。"
)


def _is_cancel(raw) -> bool:
    """判斷 client 傳來的訊息是不是「停止生成」。"""
    if not raw:
        return False
    try:
        return json.loads(raw).get("type") == "cancel"
    except (ValueError, TypeError):
        return False


def init_ws(sock):
    """由 routes/api.py 呼叫，把 WebSocket 路由掛到 api 藍圖上。"""

    @sock.route("/attraction/recognize-ws")
    def recognize_ws(ws):
        # worker 執行緒與主執行緒都可能送訊息，用鎖包起來避免 frame 交錯
        send_lock = threading.Lock()
        closed = {"value": False}

        def send(payload: dict):
            with send_lock:
                if closed["value"]:
                    return
                try:
                    ws.send(json.dumps(payload, ensure_ascii=False))
                except Exception:
                    closed["value"] = True

        try:
            # ---- 1. 第一個 frame：中繼資料（文字） ----
            raw_meta = ws.receive()
            if raw_meta is None:
                return
            try:
                meta = json.loads(raw_meta)
            except (ValueError, TypeError):
                send({"type": "error", "message": "中繼資料格式錯誤"})
                return

            # ---- 2. 第二個 frame：圖片位元組（二進位） ----
            image_bytes = ws.receive()
            if not isinstance(image_bytes, (bytes, bytearray)):
                send({"type": "error", "message": "沒有收到圖片資料"})
                return
            if len(image_bytes) > MAX_IMAGE_BYTES:
                send({"type": "error", "message": "圖片檔案過大（上限 8MB）"})
                return

            # ---- 3. 驗證 ----
            mime_type = meta.get("mime") or mimetypes.guess_type(meta.get("filename", ""))[0]
            if mime_type not in ALLOWED_MIME_TYPES:
                send({"type": "error", "message": "只支援 JPG、PNG、WEBP、HEIC 或 HEIF 圖片"})
                return

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                send({"type": "error", "message": "伺服器尚未設定 GEMINI_API_KEY"})
                return

            send({"type": "status", "message": "圖片已接收，開始辨識"})

            # ---- 4. worker 執行緒：跑 Gemini 串流、逐段送出 ----
            cancel_event = threading.Event()
            done_event = threading.Event()

            def worker():
                try:
                    client = genai.Client(api_key=api_key)
                    image_part = genai.types.Part.from_bytes(
                        data=bytes(image_bytes),
                        mime_type=mime_type,
                    )
                    stream = client.models.generate_content_stream(
                        model="gemini-2.5-flash",
                        contents=[image_part, PROMPT],
                    )
                    for chunk in stream:
                        if cancel_event.is_set():
                            try:
                                stream.close()  # 中止與 Gemini 的上游串流
                            except Exception:
                                pass
                            return
                        if chunk.text:
                            send({"type": "delta", "text": chunk.text})
                    if not cancel_event.is_set():
                        send({"type": "done"})
                except Exception as error:
                    if not cancel_event.is_set():
                        send({"type": "error", "message": f"景點辨識失敗：{error}"})
                finally:
                    done_event.set()

            threading.Thread(target=worker, daemon=True).start()

            # ---- 5. 主執行緒：聽前端訊息，直到 worker 跑完或收到 cancel ----
            while not done_event.is_set():
                try:
                    msg = ws.receive(timeout=0.5)  # 每 0.5 秒醒來看一次
                except Exception:
                    cancel_event.set()  # 連線關閉（例如使用者關掉分頁）
                    break
                if _is_cancel(msg):
                    cancel_event.set()
                    # 立刻回覆，不必等 worker 把當前這個 chunk 讀完
                    send({"type": "stopped", "message": "已停止生成"})
                    break

        except Exception as error:
            send({"type": "error", "message": f"景點辨識失敗：{error}"})
        finally:
            with send_lock:
                closed["value"] = True
