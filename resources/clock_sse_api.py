"""SSE 伺服器時鐘 —— 每秒推送一次伺服器端時間

示範 SSE（Server-Sent Events）推送資料的完整格式：
  : 這是註解            → 冒號開頭的行是註解，不會觸發事件，常用來維持連線
  event: show          → 自訂事件名稱，取代預設的 message 事件
  id: 1                → 這次事件的 ID；瀏覽器斷線重連時會用 Last-Event-ID 帶回來
  retry: 5000          → 若連線中斷，瀏覽器等 5000 毫秒再自動重連
  data: 16:24:35       → 事件資料本體
  （空白行 \n\n）        → 兩個換行代表「一則事件結束」

回應標頭 Content-Type 必須是 text/event-stream，內容為 UTF-8。

注意：這裡用一般 Flask view function（非 flask_restful 的 Resource），
因為 Resource 會把回傳值序列化成 JSON，不適合串流。
"""

import time
from datetime import datetime

from flask import Response, stream_with_context


def clock_stream():
    @stream_with_context
    def event_stream():
        event_id = 0
        try:
            while True:
                event_id += 1
                now = datetime.now().strftime("%H:%M:%S")

                # 依 SSE 格式一行一行組出來，最後用空白行（\n\n）結束這則事件
                yield (
                    ": server clock tick\n"      # 註解行（保持連線、給人看的）
                    "event: show\n"               # 自訂事件名，取代 message
                    f"id: {event_id}\n"           # 最後一次事件 ID
                    "retry: 5000\n"               # 斷線後 5 秒重連
                    f"data: {now}\n\n"            # 資料本體
                )

                time.sleep(1)                     # 每隔一秒推一次
        except GeneratorExit:
            # 瀏覽器關閉連線時會走到這裡，正常結束即可
            pass

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",   # 不要快取串流
            "X-Accel-Buffering": "no",     # 提示反向代理不要緩衝，立即轉發
        },
    )
