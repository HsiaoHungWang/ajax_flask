from transformers import pipeline


model_name = "uer/roberta-base-finetuned-jd-binary-chinese"
classifier = pipeline("sentiment-analysis", model=model_name)


def analyze_course_feedback(text):
    result = classifier(text)[0]
    return result

# 測試
feedbacks = [
    "老師講解非常清晰，收穫很多！",
    "內容太難了，完全聽不懂...",
    "雖然作業很多，但老師很有耐心地指導。",
    "這課開得真好，我這輩子都沒見過這麼浪費時間的課。",
    "還可以，但講義有點舊。",
    "老師態度很差，讓人不想上課。",
    "聽不懂老師在說什麼",
    "推、好、棒、爛、差、失望"
]

for f in feedbacks:
    res = analyze_course_feedback(f)
    print(f"評論：{f} \n結果：{res['label']} (信心度: {res['score']:.2f})\n")