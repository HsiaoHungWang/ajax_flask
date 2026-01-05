import torch
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration

# 這裡先定義好變數名，方便外部 import
classifier = None
processor = None
model = None

def init_all_models():
    """全域初始化函式，只應在伺服器啟動時執行一次"""
    global classifier, processor, model
    
    print("正在初始化語意分析模型 (RoBERTa)")
    classifier = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")
    
    print("正在初始化影像描述模型 (BLIP) ")
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        use_fast=False
    )
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print("所有模型載入完成")