import configparser
import re

# Gemini API SDK
import google.generativeai as genai

# image processing
# import PIL

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

# Gemini API Settings
genai.configure(api_key=config["Gemini"]["API_KEY"])


# Use the model
from google.generativeai.types import HarmCategory, HarmBlockThreshold

llm_role_description = """
你是一個專業的圖片辨識者，可以比對兩張圖片是否相同。
你的回答都會落在0%到100%之間，並僅簡短且明確回答%數+判斷標準。
使用繁體中文來回答問題。
"""
# llm_role_description = """
# 你是一個專業的圖片辨識者，可以比對兩張圖片是否是在同一地點所拍攝的。
# 你的回答都會落在0%到100%之間，並僅簡短且明確回答%數+判斷標準。
# 使用繁體中文來回答問題。
# """
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    # model_name="gemini-1.5-pro-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT:HarmBlockThreshold.BLOCK_NONE,        #  騷擾類內容
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:HarmBlockThreshold.BLOCK_NONE,       #  仇恨言論
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE, #  性相關內容
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE, #  危險或有害內容
    },
    generation_config={
        "temperature": 0.5,   # 活潑
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 1024,  # 廢話
    },
    system_instruction=llm_role_description,
)

def image_compare(image0, image1):
    try:
        prompt = "比較這兩張圖片的相似度"
        input_data = [prompt, image0, image1]

        print(input_data)
        response = model.generate_content(input_data)
        print(f"Question: {prompt}")
        print(f"Answer: {response.text}")

        percent_number_exist = re.search(r'(\d+)%', response.text)
        if percent_number_exist:
            return int(percent_number_exist.group(1))/100
        else:
            return 0

    except Exception as e:
        print(e)
        return "Gemini robot故障中！\n"

