import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_course_feedback_with_gemini(text):
    prompt = f"""
    分析以下學生對課程的評論：『{text}』
    請判斷其情緒，並特別注意是否包含反諷。
    
    請嚴格以 JSON 格式回傳：
    {{
      "label": "Positive 或 Negative",
      "score": 0.0 到 1.0 的信心度,
      "reason": "為什麼這樣判斷（15字內）"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"label": "Error", "score": 0, "reason": str(e)}

# 測試
feedbacks = [
    "這課開得真好，我這輩子都沒見過這麼浪費時間的課。",
    "推、好、棒、爛、差、失望"
]

for f in feedbacks:
    res = analyze_course_feedback_with_gemini(f)
    print(f"評論：{f}")
    print(f"結果：{res['label']} (信心度: {res['score']})")
    print(f"原因：{res['reason']}\n")