from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image


processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def describe_image(image_path):
    try:
        # 讀取圖片
        raw_image = Image.open(image_path).convert('RGB')
        
        # 處理圖片
        inputs = processor(raw_image, return_tensors="pt")
        
        # 生成文字
        out = model.generate(**inputs, max_new_tokens=50)
        
        # 4. 解碼輸出
        english_text = processor.decode(out[0], skip_special_tokens=True)
        return english_text
    except Exception as e:
        return f"Error: {str(e)}"

# 測試
print(describe_image('static/avatars/dog3.jpg'))


 

