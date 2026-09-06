### Fork 本專案
1. 登入你的 GitHub 帳號。
2. 在本專案頁面的右上方，找到並點擊 「Fork」 按鈕。
3. 選擇你的個人帳號作為目的地。
4. （選擇性）你可以修改 Repository name。
5. 點擊 Create fork。

### 將專案 Clone 到本地電腦
回到你個人帳號下的該專案頁面（網址應該是 https://github.com/你的帳號/專案名稱），執行以下指令：
請將網址替換成你自己 Fork 後的專案網址

<pre>
git clone https://github.com/你的帳號/專案名稱.git
</pre>
進入專案資料夾
<pre>
cd 專案名稱
</pre>




### 如何執行本專案
1. 建立虛擬環境：`python -m venv venv`
2. 啟動環境：`venv\Scripts\activate` (Windows)
3. 安裝套件：`pip install -r requirements.txt`
4. 執行程式：`python app.py`

> 只做基本頁面（住址、會員、長條圖、地圖、SSE 時鐘、Hello WebSocket…）不需要下面的 AI 設定。
> 「景點圖片辨識」的四個頁面才需要，可以只設定其中一種。

### AI 模型設定（景點圖片辨識功能）

| 頁面 | 使用的模型 | 需要的設定 |
|------|-----------|-----------|
| `/recognize`、`/recognize-stream`、`/recognize-ws` | Google Gemini（雲端 API） | `GEMINI_API_KEY` |
| `/recognize-local` | 本機 Ollama 視覺模型 | 安裝 Ollama 並下載模型 |

這些設定是透過**環境變數**讀取的（`os.getenv`），沒設定時對應頁面會回傳提示訊息（例如「伺服器尚未設定 GEMINI_API_KEY」、「連不上 Ollama」），其他頁面不受影響。

#### A. 使用 Gemini（雲端）

1. 到 [Google AI Studio](https://aistudio.google.com/apikey) 申請一組免費 API 金鑰。
2. 在「**執行 `python app.py` 的同一個終端機**」設定環境變數，再啟動程式：

   PowerShell：
   ```powershell
   $env:GEMINI_API_KEY = "你的金鑰"
   python app.py
   ```

   cmd：
   ```cmd
   set GEMINI_API_KEY=你的金鑰
   python app.py
   ```

   要每次開機都生效（設定一次即可，設完要重開終端機 / VS Code）：
   ```powershell
   # 方法一：setx（簡單，但值有長度上限）
   setx GEMINI_API_KEY "你的金鑰"

   # 方法二：.NET API（推薦，無長度限制，"User" 表示只設定目前使用者）
   [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "你的APIKEY字串", "User")
   ```

> ⚠️ 金鑰請勿寫進程式碼或 commit 上 GitHub。

#### B. 使用地端模型（Ollama）

1. 安裝 [Ollama](https://ollama.com/download)（Windows 有安裝檔，裝好會在背景常駐 `http://localhost:11434`）。
2. 下載一個「看得懂圖」的視覺模型：
   ```powershell
   ollama pull qwen2.5vl:3b
   ```
3. 直接 `python app.py` 即可，`/recognize-local` 會自動連本機 Ollama。

可用環境變數覆蓋預設值（用法同上，在啟動終端機設定）：

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 服務位址 |
| `OLLAMA_MODEL` | `qwen2.5vl:3b` | 使用的模型（可換 `qwen2.5vl:7b`、`llava` 等） |

> 首次辨識要等模型載入記憶體；純 CPU 環境可能十幾秒起跳，屬正常現象。

### 專案架構
* models/：定義資料庫模型（SQLAlchemy Classes）。存放資料表結構與屬性定義的檔案。

* resources/：存放 Flask-RESTful 的 Resource 類別。這裡負責編寫 API 的邏輯處理，例如 GET、POST 等方法的具體實作。

* routes/：定義應用程式的路由與 Blueprint（藍圖）。負責將網址路徑（URL）映射到對應的處理函式或 Resource。

* static/：存放靜態資源檔案。包括 CSS 樣式表、JavaScript 腳本、圖片以及前端上傳的檔案等。

* templates/：存放 Jinja2 HTML 模板檔案。這是後端渲染網頁時所使用的 HTML 範本。

* venv/：Python 虛擬環境。存放專案獨立的套件庫，確保開發環境的一致性（此目錄通常不進行版本控制）。

* .env：環境變數設定檔。用於存放敏感資訊（如 Secret Key、資料庫連線字串、API 密鑰等）。

* .gitignore：Git 忽略清單。指定哪些檔案（如 venv/、__pycache__/、.env、.db 等）不應上傳至 GitHub。

* app.py：應用程式的入口點。負責初始化 Flask App、載入配置、註冊藍圖（Blueprint）並啟動伺服器。

* mydb.db：SQLite 資料庫檔案。存放專案的實體資料。

* README.md：專案說明文件（即本檔案）。

* requirements.txt：專案依賴套件清單。記錄專案運行所需的所有 Python 套件及其版本，方便環境部署。
