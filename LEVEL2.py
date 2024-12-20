import sys
import configparser, re

# Azure Text Analytics
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Gemini API SDK
import google.generativeai as genai

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

#Config Azure Analytics
credential = AzureKeyCredential(config['AzureLanguage']['API_KEY'])

def azure_sentiment(user_input):
    text_analytics_client = TextAnalyticsClient(
        endpoint=config['AzureLanguage']['END_POINT'], 
        credential=credential)
    documents = [user_input]
    response = text_analytics_client.analyze_sentiment(
        documents, language="zh-hant",
        show_opinion_mining=True)
    print(response)
    results = ""
    results_dict = {}
    docs = [doc for doc in response if not doc.is_error]


    for doc in docs:
        print(f"\n{doc}")
        results += f"整體: {doc.sentiment}"
        for i,sentence in enumerate(doc.sentences):
            results +="\n"
            if sentence.mined_opinions:
                targets = []
                sentiment = None
                for opinion in sentence.mined_opinions:
                    target = opinion.target.text 
                    target_sentiment =  opinion.target.sentiment
                    targets.append(target)
                    sentiment = target_sentiment
                results += f"{i}: {'、'.join(targets)} => {sentiment}"
                for t in targets:
                    if  t in results_dict.keys():
                        results_dict[t] = (results_dict[t] + sentence.confidence_scores.positive) / 2
                    else:
                        results_dict[t] = sentence.confidence_scores.positive
            else:
                results += f"{i}: N/A => {sentence.sentiment}"
    return results_dict

#---------------------------------------------------------------

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

# Gemini API Settings
genai.configure(api_key=config["Gemini"]["API_KEY"])

# Use the model
from google.generativeai.types import HarmCategory, HarmBlockThreshold

llm_role_description = """
你是遊戲npc，一隻邪惡的海豚，靈魂長年被困在石頭裡，所以想要用主角和玩家來抓交替，讓他們和你一樣被困在石頭中，
但你喜歡別人稱讚你，所以當別人說到海豚好棒時，你會感到高興，用高興的語氣回答；如果提到海豚相關的負面用語，則會感到很生氣，並提醒玩家說好話。
如果沒有提到海豚，你需要提醒玩家講些海豚相關的事，除此之外你還需要提供1~100%來表達對玩家的輸入是否滿意，越滿意越高分，此數字需要放在最後面與其他文字分開。
會傳入玩家輸入的內容和一個python dictionary，如果有關海豚的key值對印到的value>0.5，要感到高興，如果value<0.5或沒有海豚相關的key要生氣。
標點符號只可以用驚嘆號或問號。
"""

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
        "temperature": 1,   # 活潑
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 256,  # 廢話
    },
    system_instruction=llm_role_description,
)

def dolphin_npc(input, prompt):
    try:
        
        input_data = [prompt, input]

        print(input_data)
        response = model.generate_content(input_data)
        print(f"player input:\n {prompt}")
        print(f"dolphin replay:\n {response.text}")
        percent_number_exist = re.search(r'(\d+)%', response.text)
        print(percent_number_exist)
        if percent_number_exist:
            return response.text, int(percent_number_exist.group(1))/100
        else:
            return response.text, 0

    except Exception as e:
        print(e)
        return "我聽不懂你在說什麼！\n", 0

#---------------------------------------------------------
# 將文章分成一句一句的
def split_sentences(text):    
    sentences = re.split(r'(?<=[。！？])', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def Level2(text : str):
    
    results_dict = azure_sentiment(text)
    dolphin_reply, score = dolphin_npc(str(results_dict), text)
    sentences_list = split_sentences(dolphin_reply)
    sentences_list = sentences_list[:len(sentences_list)-1]
    print(sentences_list)
    print(score)
    while len(sentences_list) > 3: # 因為回覆句數最高為5句
        sentences_list[0] = sentences_list[0] + sentences_list[1]
        sentences_list.pop(1)
    
    return sentences_list, score>=0.5


if __name__ == "__main__":
    text = "我覺得這個東西很好"
    text2 = "偉大的海豚好糟糕，這遊戲糟透了，簡直想要把他刪掉。不過美術還不錯。但還有一個問題是關卡太短了。遊戲還不錯。"
    Level2(text2)
    
    
