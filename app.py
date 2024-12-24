# self definition
from module.user import UserDataManager, User
from module.azure import azure_translate
from module.gemini import image_compare
from Web import get_bot_response
import LEVEL0 
import LEVEL1 
import LEVEL2 

# For system call
import sys
import os, json


import PIL
import PIL.Image
import random 

# For Line-bot
from flask import Flask, request, abort, render_template,jsonify
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    FollowEvent,
    UnfollowEvent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    AudioMessage,   #modify by Huang
    TextMessage,
    ImageMessage,   #modify
    VideoMessage,    #modify2
    CarouselTemplate, #modify by Ke
    CarouselColumn, #modify by Ke
)

# For Line-bot template
from linebot.v3.messaging.models import(
    MessageAction, 
    TemplateMessage, 
    ButtonsTemplate,
    ConfirmTemplate
)

import configparser
# config parser
config = configparser.ConfigParser()
config.read('config.ini')

# 開始佈署
app = Flask(__name__)

channel_access_token = config['Line']['CHANNEL_ACCESS_TOKEN']
channel_secret = config['Line']['CHANNEL_SECRET']
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

"""
Global Variable:
> FOLDER_PATH: data資料夾
> HINT: 每一關的提示詞
> userDB: 存所有user的資料
> user: User的內別，data member有 userID、lang、level、HP、timestamp
* 更改 user 的內容時，都會影響到存取的內容(僅有更改語言、關卡回合才能進行更動)
"""
FOLDER_PATH = config['Path']['FOLDER_PATH']
HINT = ("通關密語：遊戲開始", "通關密語：關卡1", "通關密語：發生在二一石", "通關密語：去或不去", "通關密語：機會或命運", "通關密語：海豚1", "通關密語：海豚2", "通關密語：海豚3", "通關密語：二一石拍照", "通關密語：基哥1","通關密語：基哥2","通關密語：教室拍照", "通關密語：沒問題", "通關密語：海豚", "通關密語：下樓", "通關密語：骰子", "通關密語：223353227") #modify by Huang
userDB = UserDataManager(FOLDER_PATH)

@app.route("/callback", methods=['POST'])
def callback():
    print("\n----------------------------------------------------------------------------------")
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body + '\n')

    # with open('info.json', 'w', encoding='utf-8') as file:
    #         json.dump(json.loads(body), file, indent=4, ensure_ascii=False)

    # 取得使用者的ID
    body_dict = json.loads(body)
    userID = body_dict['events'][0]['source']['userId']

    # 將新的使用者存進database中
    if userDB.get_user_data(userID)== None:
        userDB.add_or_update_user(User(userID=userID, lang="zh-Hant", level=0))


    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 分流處理
# 文字訊息事件的處理
@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    '''
    textmessage: 放要回傳的文字內容(e.g.['Hi', 'Hello'])
    templatemessage: 放要回傳的模板(e.g.[
                                        {'altText': '文字', 'template': 'buttons_template'},
                                        {'altText': '文字', 'template': 'confirm_template'} 
                                        ])
    '''
    textmessage = []
    templatemessage = []
    photo_urls = [] #modify
    video_urls = [] #modify2
    audio_files = [] #modify by Huang
    audio_durations = [] #modify by Huang

    userID = event.source.user_id
    user = userDB.get_user_data(userID)
    this_level_add_action = user.level
    

    if event.message.text[0] == '~':
        textmessage, templatemessage = process_command(event.message.text[1:], user)

    else:
        # 針對個別事件作處理，並接收text(回覆) # modify  下面這行
        textmessage, templatemessage, photo_urls, video_urls, audio_files, audio_durations = process_event(event.message.text, user) #modify by Huang
        if user.lang != "zh-Hant":
            # translate
            for i in range(len(textmessage)):
                textmessage[i] = azure_translate(text=textmessage[i], target_language=user.lang)

    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 將所有要透過linebot回傳的內容，全都放進 messages中
        messages = [TextMessage(text=text) for text in textmessage]
        print(f"\n{messages}")
        print("LEVEL:", user.level)
        # modify by Huang 下面 (LEVEL0 語音訊息)---------------------------------------------------------
        if event.message.text == "遊戲開始" and user.level == 1 and this_level_add_action == 0:
            audio_duration = LEVEL0.azure_speech(user.lang)
            messages.insert(0, AudioMessage(
            originalContentUrl=config["Deploy"]["URL"]+"/static/outputaudio.wav", duration=audio_duration))
        # modify by Huang 上面 (LEVEL0 語音訊息)---------------------------------------------------------  
        # modify by Huang 下面 (LEVEL1 語音訊息)---------------------------------------------------------
        if event.message.text == "關卡1" and user.level == 2 and this_level_add_action == 1: # 不能和老婆婆寫在一起因為要insert
            j = 1
            for i in range(len(audio_files)):
                messages.insert(j, AudioMessage(
                    originalContentUrl = f"{config['Deploy']['URL']}/{audio_files[i]}",
                    duration = audio_durations[i]
                ))
                j += 2
            audio_files.clear()
            audio_durations.clear()
        # modify by Huang 上面 (LEVEL1 語音訊息)---------------------------------------------------------
        # modify by Huang 下面 (LEVEL2 老婆婆語音訊息)----------------------------------------------------
        if (event.message.text == "去" and user.level == 4 and this_level_add_action == 3) or (event.message.text == "223353227" and user.level == 7 and this_level_add_action == 6):
            messages.append(AudioMessage(
                originalContentUrl = f"{config['Deploy']['URL']}/{audio_files[0]}",
                duration = audio_durations[0]
            ))
            audio_files.clear()
            audio_durations.clear()
        # modify by Huang 上面 (LEVEL2 老婆婆語音訊息)---------------------------------------------------------
        # modify by Huang 下面 (LEVEL4 老婆婆語音訊息)---------------------------------------------------------
        if event.message.text == "命運" and user.level == 5 and this_level_add_action == 4:
            messages.insert(1, AudioMessage(
                originalContentUrl = f"{config['Deploy']['URL']}/{audio_files[0]}",
                duration = audio_durations[0]
            ))
            audio_files.clear()
            audio_durations.clear()
        # modify by Huang 上面 (LEVEL4 老婆婆語音訊息)---------------------------------------------------------

        for tm in templatemessage:
            messages.append(TemplateMessage(
                alt_text=tm["altText"], 
                template=tm["template"])
                )
        # modify 下面 ---------------------------------------------------------
        for photo_url in photo_urls:
            messages.append(ImageMessage(
                            original_content_url= photo_url,
                            preview_image_url= photo_url
                        ))
        # modify 上面 ---------------------------------------------------------

        #modify2下面-----------
        for video_url, preview_image_url in video_urls: 
            messages.append(VideoMessage(
                original_content_url=video_url,  # 视频文件的直接 URL
                preview_image_url=preview_image_url  # 视频预览图 URL
            ))
        #modify2上面-----------
        if user.level == 19:
            user.level = 16
            messages.append(TextMessage(text="但別忘了打開你的寶箱，裡面有著一張名片寫著未知的電話和人名，他正是一名鎖匠。"))
            messages.append(TextMessage(text="請輸入：名片上的電話號碼(請輸入數字，不需要\"-\")"))
            messages.insert(1, ImageMessage(
                        original_content_url= 'https://imgur.com/jwD29E6.png',
                        preview_image_url= 'https://imgur.com/jwD29E6.png'
                    ))
        elif user.level == 20:
            TemplateMessage_obj = restart_game(user)
            messages.append(TemplateMessage_obj)
        # Modify by Ke  ------------------------ 修改部分下列code ------------------------ 
        # game over message
        if user.HP < 1 and user.state == False:
            print(user.card)
            if user.card == True and user.level > 11: # 有鎖匠卡的話
                user.state = True
                user.level = 16
                messages = []
                messages.append(TextMessage(text="Game Over！生命已歸0"))
                messages.append(TextMessage(text="但別忘了打開你的寶箱，裡面有著一張名片寫著未知的電話和人名，他正是一名鎖匠。"))
                messages.append(TextMessage(text="請輸入：名片上的電話號碼"))
                messages.insert(1, ImageMessage(
                            original_content_url= 'https://imgur.com/jwD29E6.png',
                            preview_image_url= 'https://imgur.com/jwD29E6.png'
                        ))
            else:
                TemplateMessage_obj = restart_game(user)
                messages = []
                messages.append(TextMessage(text="Game Over！生命已歸0"))
                if user.card == True and user.level < 12:
                    messages.append(TextMessage(text="雖然你的寶箱還沒使用，但寶箱上有寫「第三關開始後才能開」！"))
                messages.append(TemplateMessage_obj)
        # restart game message
        elif user.HP >= 0 and user.level == 17: # modify by Huang
            TemplateMessage_obj = restart_game(user)
            # if len(messages) >= 4:
            #     messages = messages[1:]
            messages.append(TextMessage(text="恭喜你全數通關！拿到鑰匙後你現在可以去把後門打開了！"))
            messages.append(TemplateMessage_obj)
        # Modify by Ke  ------------------------ 修改部分上列code ------------------------ 

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )
# Modify by Ke  ------------------------ 修改部分下列code ------------------------           
# 命令指令集
def process_command(command: str, user):
    target_languages = {"0": "en", "1": "zh-Hant", "2": "zh-Hans", "3": "ja", "4": "ko"}
    languages = ["English", "Tradional Chinese", "Simplified Chinese", "Japanese", "Korean"]
    if command == "help":
        carousel_template = CarouselTemplate(
            # actions的數量要一致
                columns=[
                    CarouselColumn(
                        title='Feature',
                        text='1',
                        actions=[
                            MessageAction(label='Get Map', text='~map'),
                            MessageAction(label='Get HP', text='~hp'),
                        ]
                    ),
                    CarouselColumn(
                        title='Feature',
                        text='2',
                        actions=[
                            MessageAction(label='Get Hint', text='~hint'),
                            MessageAction(label='Set Language', text='~lang')
                        ]
                    ),
                ]
            )
        return ["You can use the following features  to operate!"], [{"altText": "獲得功能指令", "template": carousel_template}]
    
    elif command == "hint":
        text = HINT[user.level]
        if user.lang != "zh-Hant":
                text = azure_translate(text=text, target_language=user.lang)
        return [text], []
    
    elif command == "lang":
        buttons_template = ButtonsTemplate(
            title='Language Selection',
            thumbnail_image_url='https://pgw.udn.com.tw/gw/photo.php?u=https://uc.udn.com.tw/photo/2024/05/20/0/29694296.jpg&x=0&y=0&sw=0&sh=0&exp=3600&w=832',
            text='Please select the following operation',
            # 最多四個按鈕
            actions=[
                MessageAction(label=languages[0], text='~0'),
                MessageAction(label=languages[1], text='~1'),
                MessageAction(label=languages[2], text='~2'),
                MessageAction(label=languages[3], text='~3'),
                # URIAction(label='前往GOOGLE', uri='https://www.google.com'),
                # PostbackAction(label='點擊按鈕', data='button_clicked')
                # 可以修改為自己想要的actions
            ]
        )

        return ["\n".join(f"{i}: {v}" for i, v in enumerate(languages))], [{"altText": "Modify language instructions", "template": buttons_template}]
    
    elif command in target_languages:
        user.lang = target_languages[command]
        userDB.save(user)
        return [f"Set Language: {languages[int(command)]} successfully!"], []
    
    elif command == "map":
        level_map = {0: 0, 1: 0, 2: 1, 3: 1.5, 4: 1.5, 5: 2, 6: 2, 7: 2, 8: 2.5, 9: 3, 10: 3, 11: 3.5, 12: 4, 13: 4, 14: 4, 15: 5} #modify by Huang
        return [f"Current level: {level_map[user.level]}"], []
    elif command == "hp":
        return [f"Current hp: {user.HP}"], []
    else:
        return ['Error Command! \nPlease use "~help" to query command instrunctions!'], []  
# Modify by Ke  ------------------------ 修改部分上列code ------------------------ 

# 文字事件的處理可以寫在這(各個關卡)
def process_event(text: str, user):
    place = ["遊戲開始", "極品王", "海豚1", "海豚2", "海豚3", "二一石拍照", "基哥1","基哥2","沒問題","地圖連接","上下樓","骰子","該你了"] # modify by Huang
    
    try:
        level_event = {0:level0, 1:level1, 2:level2, 3:level3, 4:level4, 5:level5, 6:level6, 7:level7, 8:level8, 9:level9, 10:level10 ,11:level11, 12:level12, 13:level13, 14:level14, 15:level15, 16:level16} # modify by Huang
        is_pass, textmessage, templatemessage, photo_urls ,video_urls, audio_files, audio_durations= level_event[user.level](text, user) # modify by Huang

        # Modify by Ke  ------------------------ 修改部分下列code ------------------------ 
        # 是否進入下一關卡
        if is_pass :
            print(f"{user.userID} finished level{user.level}\n")
            user.level = user.level + 1
            if user.level < 17: # modify by Huang
                userDB.save(user)
        # Modify by Ke  ------------------------ 修改部分上列code ------------------------ 
        
        return textmessage, templatemessage, photo_urls, video_urls, audio_files, audio_durations # modify by Huang
    
    except Exception as e:
        print(e)

# modify 下面 ---------------------------------------------------------

# "遊戲開始"
def level0(text: str, user):
    if text == "遊戲開始":
        return True, ["聽完廣播後，你看向了完全不認識的主角說：我看妳骨骼驚奇，我的夥伴就決定是你了！於是你和主角一同踏上了尋找鑰匙的旅程。", "請輸入：「關卡1」來開啟第一關。"], [], ['https://imgur.com/DYnq0Zo.png'], [], [], []
    elif text == "不要繼續":
        return False, ["掰掰！👋"], [], [], [], [], []
    elif text == "我還是回家睡睡好了":
        return False, ["再考慮一次麻~"], [], [], [], [], []
    else:
        return False, ["再試一次"], [], [], [], [], []

# 去極品王
def level1(text: str, user):
    if text == "關卡1":
        file_name_list = []
        duration_list = []
        # 生成第一段語音
        voice_map_1 = {
        "en": "en-US-JennyNeural",
        "zh-Hant": "zh-CN-XiaoshuangNeural", 
        "zh-Hans": "zh-CN-XiaoshuangNeural",
        "ja": "ja-JP-NanamiNeural",    
        "ko": "ko-KR-SunHiNeural",
        }
        if user.lang in voice_map_1:
            selected_voice1 = voice_map_1[user.lang]

        text_speech1 = "感覺可以從後門附近開始調查，你覺得要先調查哪裡呢？不然我們先去極品王，買個飲料吧"
        file_name1, duration1 = LEVEL1.azure_speech(text_speech1, user.lang, selected_voice1, "1")
        file_name_list.append(file_name1)  # 將檔名追加到清單
        duration_list.append(duration1)   # 將持續時間追加到清單

        # 生成第二段語音
        voice_map_2 = {
        "en": "en-US-JaneNeural",
        "zh-Hant": "zh-CN-XiaoxiaoNeural", 
        "zh-Hans": "zh-CN-XiaoxiaoNeural",
        "ja": "ja-JP-MayuNeural",    
        "ko": "ko-KR-SeoHyeonNeural",
        }
        if user.lang in voice_map_2:
            selected_voice2 = voice_map_2[user.lang]
        
        text_speech2 = "你們有聽過一個傳說嗎？以前元智有養海豚在五館前面的圓環，所以吉祥物是海豚，那隻海豚幾年前被月型石出來的魔物攻擊，導致海豚會抓交替，人碰到會變石頭，為了避免魔物再度傷人，才又搬來一塊石頭斜靠在月型石旁，並且題字鎮壓。"
        file_name2, duration2 = LEVEL1.azure_speech(text_speech2, user.lang, selected_voice2, "2")
        file_name_list.append(file_name2)  # 將第二段檔名追加到清單
        duration_list.append(duration2)

        # 傳說發生地點
        buttons_template = ButtonsTemplate(
            thumbnail_image_url='https://imgur.com/3V6yAe2.png', # 極品王店員圖
            text="以上傳說是發生在甚麼地點？",
                actions=[
                    MessageAction(label='二一石', text="發生在二一石"),
                    MessageAction(label='牡丹亭', text="發生在牡丹亭"),
                    MessageAction(label='有庠紀念花園', text="發生在有庠紀念花園")
                ]
        )
        return True, ["主角：", "極品王店員："], [{"altText": "是否再次接受此任務", "template": buttons_template}], [], [], file_name_list, duration_list
    else:
        return False, ["**聽清楚題目，請再試一次**"], [], [], [], [], []

def level2(text: str, user):  
    # 傳說發生地點
    buttons_template = ButtonsTemplate(
        text="以上傳說是發生在甚麼地點？",
            actions=[
                MessageAction(label='二一石', text="發生在二一石"),
                MessageAction(label='佛雕禪詩', text="發生在佛雕禪詩"),
                MessageAction(label='有庠紀念花園', text="發生在有庠紀念花園")
            ]
    )
    buttons_template2 = ButtonsTemplate(
        # thumbnail_image_url='https://imgur.com/fz4zgDb.png', # 網球場圖
        text="是否要去網球場看看？",
            actions=[
                MessageAction(label='去', text="去"),
                MessageAction(label='不去', text="不去")
            ]
    )

    if text == "發生在二一石":
        return True, ["**關卡1完成！**", \
                      "於是你們決定前往二一石，但現在已是深夜，你和主角兩人並肩走在漆黑的道路上，想到剛剛的傳說不經讓你們背脊發涼，此時恰好路過空蕩蕩的網球場，好像聽到有人在講話。"], [{"altText": "是否再次接受此任務", "template": buttons_template2}], [], [], [], []
    else:
        user.HP-=1
        userDB.save(user)
        return False, ["**你答錯了，被極品王店員打一拳，生命值-1，請再試一次**"], [{"altText": "是否再次接受此任務", "template": buttons_template}], ['https://i.imgur.com/dx1xWXj.png'], [], [], [] # 巴掌圖

# 去不去操場
def level3(text: str, user):
    buttons_template2 = ButtonsTemplate(
        # thumbnail_image_url='https://imgur.com/fz4zgDb.png' # 網球場圖
        text="是否要去網球場看看？",
            actions=[
                MessageAction(label='去', text="去"),
                MessageAction(label='不去', text="不去")
            ]
    )
    # 生成神秘老婆婆語音
    file_name_list = []
    duration_list = []

    voice_map = {
        "en": "en-US-NancyNeural",
        "zh-Hant": "zh-CN-XiaoqiuNeural", 
        "zh-Hans": "zh-CN-XiaoqiuNeural",
        "ja": "ja-JP-ShioriNeural",    
        "ko": "ko-KR-YuJinNeural",
        }
    if user.lang in voice_map:
        selected_voice = voice_map[user.lang]

    text_speech = "同學，算張塔羅牌吧。"
    file_name1, duration1 = LEVEL1.azure_speech(text_speech, user.lang, selected_voice, "3")
    file_name_list.append(file_name1)  # 將檔名追加到清單
    duration_list.append(duration1)

    if text == "去":
        buttons_template3 = ButtonsTemplate(
            thumbnail_image_url='https://imgur.com/fz4zgDb.png', # 機會命運圖
            text="選一張牌",
                actions=[
                    MessageAction(label='機會', text="機會"),
                    MessageAction(label='命運', text="命運")
                ]
        )
        user.level = 3
        return True, ["進入空蕩蕩的網球場中，遇到了一位老婆婆。", "老婆婆："], [{"altText": "是否再次接受此任務", "template": buttons_template3}], ['https://imgur.com/k2QtNw5.png'], [], file_name_list, duration_list
    else: # 不去
        user.level = 4
        return True, ["你與主角繼續前往二一石一探究竟，突然一陣陰風吹過，一隻邪惡的海豚赫然出現在二一石上，一鰭擋住了你的去路。", \
                      "主角：根據傳說，二一石海豚最喜歡的就是別人稱讚他了！一直稱讚他或許就能通過了。\n**關卡2開始！**"], [], ["https://imgur.com/ixzdw7s.png"], [], [], [] # 石頭海豚

# "去網球場" 
def level4(text: str, user):
    # 生成神秘老婆婆語音
    file_name_list = []
    duration_list = []

    voice_map = {
        "en": "en-US-NancyNeural",
        "zh-Hant": "zh-CN-XiaoqiuNeural", 
        "zh-Hans": "zh-CN-XiaoqiuNeural",
        "ja": "ja-JP-ShioriNeural",    
        "ko": "ko-KR-YuJinNeural",
        }
    if user.lang in voice_map:
        selected_voice = voice_map[user.lang]

    text_speech = "你是特殊的人，去網球場的操場看看吧，命運在那兒等著你。"
    file_name1, duration1 = LEVEL1.azure_speech(text_speech, user.lang, selected_voice, "4")
    file_name_list.append(file_name1)  # 將檔名追加到清單
    duration_list.append(duration1)

    if text == "機會":
        user.HP+=1
        return True, ["恭喜你獲得了加一條命的機會，已將你的命加了一條。走吧，繼續你的旅程吧！", \
                      "於是你與主角繼續前往二一石一探究竟，突然一陣陰風吹過，一隻邪惡的海豚赫然出現在二一石上，一鰭擋住了你的去路。", \
                      "主角：根據傳說，二一石海豚最喜歡的就是別人稱讚他了！一直稱讚他或許就能通過了。\n**關卡2開始！**"], [], ["https://imgur.com/ixzdw7s.png"], [], [], []
    elif text == "命運":
        user.card = True
        return True, ["老婆婆突然露出微笑：", \
                      "於是你和主角前往了操場，拿到神秘寶箱後，上面寫著「第三關開始才能使用」，因此你們拿著寶箱繼續前往二一石一探究竟，突然一陣陰風吹過，一隻邪惡的海豚赫然出現在二一石上，一鰭擋住了你的去路。", \
                      "主角：根據傳說，二一石海豚最喜歡的就是別人稱讚他了！一直稱讚他或許就能通過了。\n**關卡2開始！**"], [], ["https://imgur.com/ixzdw7s.png"], [], file_name_list, duration_list

#  "海豚1"
def level5(text: str, user):
    sentences_list, flag = LEVEL2.Level2(text)
    print("1\n")
    print(sentences_list)
    if flag:
        sentences_list.append("再多說一點！再多說一點！")
        return flag, sentences_list, [], [], [], [], []
    else:
        # 扣血條
        user.level = 5 # modify by Huang
        user.HP-=1
        userDB.save(user)
        sentences_list.append("**你被海豚甩尾，生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], [], [], []  # 海豚甩尾圖

# "海豚2"
def level6(text: str, user):
    sentences_list, flag = LEVEL2.Level2(text)
    print("2\n")
    print(sentences_list)
    if flag:
        sentences_list.append("哇～真是太令我開心了！再多說一點！")
        return flag, sentences_list, [], [], [], [], []
    else:
        # 扣血條
        user.level = 5 # modify by Huang
        user.HP-=1
        userDB.save(user)
        sentences_list.append("**你被海豚甩尾，生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], [], [], []  # 海豚甩尾圖

# "海豚3"
def level7(text: str, user):
    sentences_list, flag = LEVEL2.Level2(text)
    print("3\n")
    print(sentences_list)
    if flag:
        return flag, ["**關卡2完成！**", "海豚決定不抓交替，放你一馬。", "原來機關就在二一石之間！", "請將手放置在二一石上拍照以啟動傳送門。"], [], ['https://imgur.com/92DyBMW.png'], [], [], [] # 二一石手圖
    else:
        # 扣血條
        user.level = 5 # modify by Huang
        user.HP-=1
        userDB.save(user)
        sentences_list.append("**你被海豚甩尾，生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], [], [], []  # 海豚甩尾圖


# Modify by Ke  ------------------------ 修改部分下列code ------------------------ 
# 與二一石拍照比對功能 (手放在 慎思 創新 石頭的中間) 
def level8(text: str, user):
        return False, ["請將手放置在二一石上拍照以啟動傳送門。"], [], [], [], [], []
# Modify by Ke  ------------------------ 修改部分上列code ------------------------ 
    
# 基哥
def level9(text: str, user):  
    # 基哥1 填空處1
    buttons_template4 = ButtonsTemplate(
        title='大數問題1',
        thumbnail_image_url='https://imgur.com/tdEr9W1.png', # 基哥so far圖
        text='填空處1該填入甚麼？',
        actions=[
            MessageAction(label="sum += num1[i]-'0'", text="sum += num1[i] - '0'"),
            MessageAction(label="sum += num1", text="sum += num1"),
        ]
    )
    # 基哥2 填空處2
    buttons_template5 = ButtonsTemplate(
            title='大數問題2',
            thumbnail_image_url='https://imgur.com/tdEr9W1.png', # 基哥so far圖
            text='請填入填空處2',
            actions=[
                MessageAction(label="(sum % 10)", text="result += (sum % 10)"),
                MessageAction(label="(sum % 10)-'0'", text="result += (sum % 10) - '0'"),
                MessageAction(label="(sum % 10)+'0'", text="result += (sum % 10) + '0'")  
            ]
        )

    if text == "sum += num1[i] - '0'":
        return True, ["**請繼續回答填空處2**"], [{"altText": "是否再次接受此任務", "template": buttons_template5}], [], [], [], []
    else:
        user.HP-=1
        userDB.save(user)
        return False, ["**基哥覺得你要重修，生命值-1，請再試一次**"], [{"altText": "是否再次接受此任務", "template": buttons_template4}], ['https://imgur.com/otdwLqV.png'], [], [], [] # 基哥重修圖

# 基哥
def level10(text: str, user): 
    # 基哥2 填空處2
    buttons_template5 = ButtonsTemplate(
            title='大數問題2',
            thumbnail_image_url='https://imgur.com/tdEr9W1.png', # 基哥so far圖
            text='請填入填空處2',
            actions=[
                MessageAction(label="(sum % 10)", text="result += (sum % 10)"),
                MessageAction(label="(sum % 10)-'0'", text="result += (sum % 10) - '0'"),
                MessageAction(label="(sum % 10)+'0'", text="result += (sum % 10) + '0'")  
            ]
        )

    if text == "result += (sum % 10) + '0'":
        return True, ["**關卡3完成！**","基哥給你的線索是一段程式碼，請解開cout的內容，並去該教室門牌拍照。"], [], ['https://imgur.com/lIa6eKg.png'], [], [], [] # 1201提示程式碼圖
    else:
        user.HP-=1
        userDB.save(user)
        return False, ["**基哥覺得你要重修，生命值-1，請再試一次**"], [{"altText": "是否再次接受此任務", "template": buttons_template5}], ['https://imgur.com/otdwLqV.png'], [], [], [] # 基哥重修圖 

def level11(text: str, user):
        return False, ["請根據基哥給的線索，去該教室門牌拍照。"], [], [], [], [], []
# modify 上面 ---------------------------------------------------------    

# modify 下下面 ---------------------------------------------------------    
def level12(text:str, user):
    buttons_template7 = ButtonsTemplate(
        thumbnail_image_url='https://tse3.mm.bing.net/th?id=OIP.GUeLagi3xbfrJ_BxybJqKwAAAA&pid=Api&P=0&h=180', # 真相只有一個圖
        text="請觀察以下的校園地圖，你有沒有覺得圖上的藍點加上我們走過的地方，可以連成一個圖案，那個圖案是甚麼呢？",
            actions=[
                MessageAction(label='五角星', text="我覺得是五角星"),
                MessageAction(label='海豚', text="我覺得是海豚"),
                MessageAction(label='校長', text="我覺得看起來好像校長")
            ]
    )
    buttons_template8 = ButtonsTemplate(
        thumbnail_image_url='https://i.imgur.com/8LhX2ar.png', # 上下樓圖
        text='追去樓梯口，現在有兩種選擇，請問你要上樓還下樓呢？',
        actions=[
            MessageAction(label="上樓", text="我要上樓"),
            MessageAction(label="下樓", text="我要下樓")
        ]
    )
    if text == "我覺得是海豚":
            return True, ["果然跟我想的一樣！", "突然在樓梯間閃過一個黑影，似乎是拿鑰匙的人！","趕緊追上他，別讓他跑了！！"], [{"altText": "是否再次接受此任務", "template": buttons_template8}], [], [], [], []
    else:
        user.HP-=1
        userDB.save(user)
        return False, ["**我覺得好像不是欸，生命值-1，請再試一次**"], [{"altText": "是否再次接受此任務", "template": buttons_template7}], ['https://i.imgur.com/dx1xWXj.png'], [], [], [] # 巴掌

def level13(text:str, user):
    buttons_template8 = ButtonsTemplate(
        thumbnail_image_url='https://i.imgur.com/G49qJ9k.jpeg', # 上下樓圖
        text='追去樓梯口，現在有兩種選擇，請問你要上樓還下樓呢？',
        actions=[
            MessageAction(label="上樓", text="我要上樓"),
            MessageAction(label="下樓", text="我要下樓")
        ]
    )
    if text == "我要下樓":
        return True, ["**關卡4完成！關卡5開始！**","黑影停在YZU的牌子面前","竟然被你們追過來了，看來你們真的很想要這把鑰匙，好吧，我這邊有個骰子，我們輪流骰骰子，如果你的點數比我大，我就把鑰匙給你。","請輸入「骰子」來擲骰子。"], [], ['https://www.yzu.edu.tw/admin/pr/images/20220930-2.jpg'], [], [], [] #yzu+黑影
    else:
        if user.card == True:
            user.level = 18
        else:
            user.level = 19
        return True, ["失之毫釐，差之千里，黑影把鑰匙拿走了，遊戲失敗。"], [], [], [], [], []
    
player_dice = None
opponent_dice = None

def level14(text: str, user):
    global player_dice  # 使用全局變量存儲玩家的點數
    if text == "骰子":
        player_dice = random.randint(1, 6)
        video_map = {
            1: ('https://i.imgur.com/vT2sdlu.mp4', 'https://i.imgur.com/wMQZvUc.jpeg'),
            2: ('https://i.imgur.com/lr8p3Vp.mp4', 'https://i.imgur.com/nWulA95.jpeg'),
            3: ('https://i.imgur.com/qZpkQL3.mp4', 'https://i.imgur.com/MNwdRFU.jpeg'),
            4: ('https://i.imgur.com/MbdUSVr.mp4', 'https://i.imgur.com/5mC8Dp2.jpeg'),
            5: ('https://i.imgur.com/w9DhjV6.mp4', 'https://i.imgur.com/LWhp8Wt.jpeg'),
            6: ('https://i.imgur.com/eBNEUSz.mp4', 'https://i.imgur.com/j26ng7L.jpeg')
        }
        
        video_url, preview_url = video_map[player_dice]
        return True, [f"你的點數是：{player_dice}", "輸入「換你了」讓對方擲骰子。"], [], [], [(video_url, preview_url)], [], []
    else:
        return False, ["請輸入「骰子」來擲骰子。"], [], [], [], [], []

def level15(text:str, user):
    global player_dice, opponent_dice  # 使用全局變量存儲對方的點數
    if text == "換你了":
        opponent_dice = random.randint(1, 6)
        video_map = {
            1: ('https://i.imgur.com/vT2sdlu.mp4', 'https://i.imgur.com/wMQZvUc.jpeg'),
            2: ('https://i.imgur.com/lr8p3Vp.mp4', 'https://i.imgur.com/nWulA95.jpeg'),
            3: ('https://i.imgur.com/qZpkQL3.mp4', 'https://i.imgur.com/MNwdRFU.jpeg'),
            4: ('https://i.imgur.com/MbdUSVr.mp4', 'https://i.imgur.com/5mC8Dp2.jpeg'),
            5: ('https://i.imgur.com/w9DhjV6.mp4', 'https://i.imgur.com/LWhp8Wt.jpeg'),
            6: ('https://i.imgur.com/eBNEUSz.mp4', 'https://i.imgur.com/j26ng7L.jpeg')
        }
        
        video_url, preview_url = video_map[opponent_dice]
        if player_dice > opponent_dice:
            user.level = 16
            return True, [f"我的點數是：{opponent_dice}", "恭喜你贏了！鑰匙給你🗝️！"], [], [], [(video_url, preview_url)], [], []
        elif player_dice < opponent_dice:
            if user.card == True:
                user.level = 18
            else:
                user.level = 19
            return True, [f"我的點數是：{opponent_dice}", "很遺憾你輸了！"], [], [], [(video_url, preview_url)], [], []
        elif player_dice == opponent_dice:
            user.level = 14 # modify by Huang
            userDB.save(user)
            return False, [f"我的點數是：{opponent_dice}", "平手！我們在比一次吧！","輸入「骰子」擲骰子！"], [], [], [(video_url, preview_url)], [], []
    else:
        return False, ["請輸入「換你了」讓對方擲骰子"], [], [], [], [], []

def level16(text:str, user):
    if text == "223353227":
        user.card = False
        # 生成鎖匠語音
        file_name_list = []
        duration_list = []

        voice_map = {
        "en": "en-US-DavisNeural",
        "zh-Hant": "zh-CN-YunxiNeural", 
        "zh-Hans": "zh-CN-YunxiNeural",
        "ja": "ja-JP-NaokiNeural",    
        "ko": "ko-KR-GookMinNeural",
        }
        if user.lang in voice_map:
            selected_voice = voice_map[user.lang]

        text_speech = "你好，神秘老婆婆有告知我要將我所偷偷複製的鑰匙拿給撥打這支電話的人，稍後將為你送到。"
        file_name1, duration1 = LEVEL1.azure_speech(text_speech, user.lang, selected_voice, "4")
        file_name_list.append(file_name1)  # 將檔名追加到清單
        duration_list.append(duration1)
        # 鑰匙照片
        return True, ["鎖匠："], [], [], [], file_name_list, duration_list
    else:
        return False, ["您撥的是空號，請重新再撥打一次。"], [], [], [], [], []

# Modify by Ke  ------------------------ 修改部分下列code ------------------------ 
def restart_game(user):
    userDB.delete_user(user)
    confirm_template = ConfirmTemplate(
        text="是否再次接受此任務",
        actions=[
            MessageAction(label='是', text='遊戲開始'),
            MessageAction(label='否', text='不要繼續')
        ]
    )
    return TemplateMessage(
                alt_text="是否再次接受此任務", 
                template=confirm_template)

# 圖片事件的處理
@handler.add(MessageEvent, message=ImageMessageContent)
def message_image(event):
    image_file_path = ""
    message_content = None
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(
            message_id=event.message.id
        )
    

    '''
    textmessage: 放要回傳的文字內容(e.g.['Hi', 'Hello'])
    templatemessage: 放要回傳的模板(e.g.[
                                        {'altText': '文字', 'template': 'buttons_template'},
                                        {'altText': '文字', 'template': 'confirm_template'} 
                                        ])
    '''
    textmessage = []
    templatemessage = []
    photo_urls = []
    video_urls = []

    userID = event.source.user_id
    user = userDB.get_user_data(userID)
    try:
        level_event = {8:level8_image, 11:level11_image}
        if user.level in level_event:
            # 僅存符合條件的圖片
            image_file_path = userDB.save_image(user, message_content)
            # 比較相似度
            image_GT = PIL.Image.open(f"./GT/{user.level}.jpg")
            image_input = PIL.Image.open(image_file_path)
            similarity = image_compare(image_GT, image_input)

            is_pass, textmessage, templatemessage, photo_urls, video_urls = level_event[user.level](similarity=similarity)
            # 是否進入下一關卡
            if is_pass:
                print(f"Finished level{user.level}\n")
                user.level = user.level + 1
                userDB.save(user)
        else:
            textmessage.append("請輸入文字")

    except Exception as e:
        print(e)

    if user.lang != "zh-Hant":
        # translate
        for i in range(len(textmessage)):
            textmessage[i] = azure_translate(text=textmessage[i], target_language=user.lang)


    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # 將所有要透過linebot回傳的內容，全都放進 messages中
        messages = [TextMessage(text=text) for text in textmessage]
        for tm in templatemessage:
            messages.append(TemplateMessage(
                alt_text=tm["altText"], 
                template=tm["template"])
                )
        for photo_url in photo_urls:
            messages.append(ImageMessage(
                            original_content_url= photo_url,
                            preview_image_url= photo_url
                        ))

        for video_url,preview_image_url in video_urls: 
            messages.append(VideoMessage(
                original_content_url=video_url,
                preview_image_url=preview_image_url  
            ))

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )
# 與二一石拍照比對功能 (手放在 慎思 創新 石頭的中間)  # 沒寫
def level8_image(similarity):
    # 基哥1 填空處1
    buttons_template = ButtonsTemplate(
        title='大數問題1',
        thumbnail_image_url='https://imgur.com/tdEr9W1.png', # 基哥so far圖
        text='填空處1該填入甚麼？',
        actions=[
            MessageAction(label="sum += num1[i]-'0'", text="sum += num1[i] - '0'"),
            MessageAction(label="sum += num1", text="sum += num1"),
        ]
    )

    if similarity >= 0.7:
        return True, ["**關卡3開始！**", "池水清澈，微風輕拂。池邊石凳上坐著一位戴眼鏡的老年男子——基成先生，他手中拿著一台筆記型電腦，正在專注地敲著鍵盤。他抬起頭，看到玩家，露出了一絲狡黠的笑容。", \
                      "想從我這裡拿到線索，可得證明你有寫程式的基本功！\n相信大數的問題對你們來說不是問題，嘿嘿。"], [{"altText": "是否再次接受此任務", "template": buttons_template}], ['https://imgur.com/LVfRaXN.png'], [] # 程式題目圖
    else:
        return False, [f"相似度: {similarity*100}%", "再試一次"], [], [], []

# Modify by Ke  ------------------------ 修改部分上列code ------------------------ 
# modify by Huang  下面-------------------------
def level11_image(similarity):
    buttons_template = ButtonsTemplate(
        thumbnail_image_url='https://tse3.mm.bing.net/th?id=OIP.GUeLagi3xbfrJ_BxybJqKwAAAA&pid=Api&P=0&h=180', # 真相只有一個圖
        text="請觀察以下的校園地圖，你有沒有覺得圖上的藍點加上我們走過的地方，可以連成一個圖案，那個圖案是甚麼呢？",
            actions=[
                MessageAction(label='五角星', text="我覺得是五角星"),
                MessageAction(label='海豚', text="我覺得是海豚"),
                MessageAction(label='校長', text="我覺得看起來好像校長")
            ]
    )
    if similarity >= 0.7:
        return True, ["**關卡4開始！**\n你得到了一張元智校園地圖。", "在離開1201的路上，附近傳來稀稀疏疏的影片聲音，仔細聽發現怎麼有人在播柯南！影片中柯南說：我找到這次的破案關鍵了，地圖上的點可以連成一個圖案欸！", \
                        "主角：啊，好像是欸，你覺得像什麼？"], [{"altText": "是否再次接受此任務", "template": buttons_template}], ['https://i.imgur.com/e6fdYQp.jpeg'], []    
    else:
        return False, [f"相似度: {similarity*100}%", "再試一次"], [], [], []
# modify by Huang  上面-------------------------

# 追蹤/加好友的事件處理
@handler.add(FollowEvent)
def handle_follow(event):
    confirm_template = ConfirmTemplate(
            text="是否接受此任務",
            actions=[
                MessageAction(label='是', text='遊戲開始'),
                MessageAction(label='否', text='我還是回家睡睡好了')
            ]
        )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TemplateMessage(altText="是否接受此任務",
                                        template=confirm_template)]
            )
        )



# 退追/封鎖事件的處理
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userID = event.source.user_id
    user = userDB.get_user_data(userID)

    userDB.delete_user(user.userID)

              
#     ----------------------------------------------------------------------------------   For Web   ----------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/api/chat/<contact_id>", methods=["POST"])
def chat(contact_id):
    try:      
        # 取得使用者訊息
        message =  request.form.get("message", "")
        level = int( request.form.get("level", 0))  # 如果沒有提供 level，設為預設值 "default"
        image = request.files.get("image")  # 處理圖片

        if not message and not image:
            return jsonify({"error": "訊息和圖片內容為空"}), 400

        print(f"Received: message={message}, level={level}")
        # 處理圖片上傳
        image_url = None
        if image:
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_filename)
            image_url = f"/uploads/{image.filename}"

        level, textmessage, templatemessage ,photo_urls, is_pass = get_bot_response(contact_id, message, level, image_url)
        print("Success!")

        return jsonify({"message": textmessage, "level": level, "is_pass": is_pass, "templatemessage": templatemessage}), 200
    except Exception as e:
        print("error", str(e))
        return jsonify({"error": str(e)}), 500

#     ----------------------------------------------------------------------------------   For Web   ----------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001)