"""最簡單的 WebSocket Echo Server（Hello WebSocket 範例）

用 flask-sock 的 @sock.route 掛在 api 藍圖上：
    routes/api.py 已建立   sock = Sock(api_bp)
    這裡的路由 /ws/echo  →  實際網址 /api/ws/echo

Echo 的意思：收到什麼，就把「Echo: 什麼」送回去。

幾個重點觀念（對應投影片）：
  - ws.receive()：會「阻塞等待」；文字 frame 回傳 str，二進位 frame 回傳 bytes
  - ws.receive() 在連線關閉時回傳 None，要判斷後 break 跳出迴圈
  - ws.send(data)：可以送 str 或 bytes
"""


def init_echo_ws(sock):
    @sock.route("/ws/echo")
    def echo(ws):
        while True:
            message = ws.receive()      # 阻塞等待瀏覽器送訊息過來
            if message is None:         # 連線關閉
                break
            ws.send(f"Echo: {message}")  # 原樣加個前綴送回去
