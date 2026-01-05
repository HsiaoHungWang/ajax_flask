# 先安裝套件 pip install transformers

from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import os

def preload():
    
    # 載入語意模型
    pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")
    
    # 載入影像辨識模型
    model_id = "Salesforce/blip-image-captioning-base"
    BlipProcessor.from_pretrained(model_id)
    BlipForConditionalGeneration.from_pretrained(model_id)    
   

def check_preload():
    import os
    cache_path = os.path.expanduser("~/.cache/huggingface/hub")
    print(f"模型存放路徑：{cache_path}")
    print("目前已存在的模型：", os.listdir(cache_path) if os.path.exists(cache_path) else "尚未下載")

if __name__ == "__main__":
    preload()
    check_preload()