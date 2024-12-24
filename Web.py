import random
import LEVEL2

# 根據訊息內容回應不同
def get_bot_response(contact_id, user_message, level, image):
    level_event = {0:web_level0, 1:web_level1, 2:web_level2, 3:web_level3, 4:web_level4, 5:web_level5, 6:web_level6, 7:web_level7, 8:web_level8, 9:web_level9, 10:web_level10 ,11:web_level11} 
    is_pass, textmessage, templatemessage, photo_urls ,video_urls = level_event[level](user_message) #modify

    # 是否進入下一關卡
    if is_pass :
        print(f"Finished level{level}\n")
        level = level + 1
        is_pass = 1
    else:
        is_pass = 0
        
    return level, textmessage, templatemessage ,photo_urls, is_pass

# "遊戲開始"
def web_level0(text: str):
    if text == "遊戲開始":
        return True, ["**關卡1 完成!**", "你與主角決定前往二一石一探究竟，一陣陰風吹過，一隻邪惡的海豚赫然出現在二一石上，一鰭擋住了你的去路","主角: 根據我的小本本說，二一石海豚最喜歡的就是別人稱讚他了!"], [], ['https://imgur.com/ixzdw7s.png'],[] # 石頭海豚
    elif text == "我還是回家睡睡好了" or text == "我這次決定回家睡睡":
        return False, ["膽小鬼!"], [], [], []
    else:
        return False, ["再試一次"], [], [], []

#  "海豚1"
def web_level1(text: str):
    sentences_list, flag = LEVEL2.Level2(text)
    print("1\n")
    print(sentences_list)
    if flag:
        sentences_list.append("再多說一點！ 再多說一點!")
        return flag, sentences_list, [], [], []
    else:
        sentences_list.append("**你被海豚甩尾 生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], []  # 海豚甩尾圖

# "海豚2"
def web_level2(text: str):
    sentences_list, flag = LEVEL2.Level2(text)
    if flag:
        sentences_list.append("哇～ 真是太令我開心了! 再多說一點")
        return flag, sentences_list, [], [], []
    else:
        sentences_list.append("**你被海豚甩尾 生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], []  # 海豚甩尾圖

# "海豚3"
def web_level3(text: str):
    sentences_list, flag = LEVEL2.Level2(text)
    if flag:
        return flag, ["**關卡2 完成！**", "海豚決定不抓交替，放你一馬。", "原來機關就在二一石之間！", "請將手放置在二一石上拍照已啟動傳送門"], [], ['https://imgur.com/92DyBMW.png'], [] # 二一石手圖
    else:
        sentences_list.append("**你被海豚甩尾 生命值-1，請再試一次**")
        return flag, sentences_list, [], ['https://i.imgur.com/KouT1gt.png'], []  # 海豚甩尾圖

# 與二一石拍照比對功能 (手放在 慎思 創新 石頭的中間)  # 沒寫s
def web_level4(text: str):
        return False, ["請將手放置在二一石上拍照已啟動傳送門"], [], [], []

# 基哥
def web_level5(text: str):  
    if text == "sum += num1[i]-'0'":
        return True, ["**請繼續回答 填空處2**"], ["填空處1該填入甚麼?"], [], [] 
    else:
        return False, ["**基哥覺得你要重修 生命值-1，請再試一次**"], ["請填入填空處2"], ['https://imgur.com/otdwLqV.png'], [] # 基哥重修圖

# 基哥
def web_level6(text: str): 
    if text == "(sum % 10)+'0'":
        return True, ["**關卡3 完成! **","基哥給你的線索是一段程式碼，請解開cout的內容，並去該教室門牌拍照so far有沒有問題"], [], ['https://imgur.com/lIa6eKg.png'], [] # 1201提示程式碼圖
    else:
        return False, ["**基哥覺得你要重修 生命值-1，請再試一次**"], [], ['https://imgur.com/otdwLqV.png'], [] # 基哥重修圖 

def web_level7(text:str):
    if text == "沒問題":
        return True, ["**關卡4 開始!**", "在走去1201的路上，附近傳來稀稀疏疏的影片聲音，仔細聽發現怎麼有人在播柯南！影片中柯南說：我找到這次的破案關鍵了，地圖上的點可以連成一個圖案欸", \
                      "主角：啊，好像是欸，你覺得像什麼?"], [], ['https://i.imgur.com/e6fdYQp.jpeg'], [] # 學校地圖
    else:
        return False, ["沒問題請說沒問題"], [], [], []

def web_level8(text:str):
    if text == "海豚":
        return True, ["**果然跟我想的一樣！我們趕快去1201吧**","快到1201門口時，突然閃過一個黑影，似乎是拿鑰匙人!!","趕緊追上他，別讓他跑了"], [], [], []
    else:
        return False, ["**我覺得好像不是欸 生命值-1，請再試一次**"], [], ['https://i.imgur.com/dx1xWXj.png'], [] # 巴掌
    
def web_level9(text:str):
    if text == "下樓，那腳印一定是障眼法!":
        return True, ["**關卡4通過，關卡5開始**","黑影停在YZU的牌子面前","竟然被你們追過來了，看來你們真的很想要這把鑰匙，好吧，我這邊有個骰子，我們輪流骰骰子，如果你的點數比我大，我就把鑰匙給你","請輸入'骰子'來擲骰子"], [], ['https://www.yzu.edu.tw/admin/pr/images/20220930-2.jpg'], [] #yzu+黑影
    else:
        #道具部分還沒做...，Gameover沒有停下來
        return False , ["失之毫釐，差之千里，黑影把鑰匙拿走了", "遊戲失敗 Gameover"], [], [], []
    
player_dice = None
opponent_dice = None

def web_level10(text: str):
    global player_dice  # 使用全局變量存儲玩家的點數
    if text == "骰子":
        player_dice = random.randint(1, 6)     
        return True, [f"你的點數是: {player_dice}", "輸入 '換你了' 讓對方擲骰子"], [player_dice], [], []
    else:
        return False, ["請輸入 '骰子' 來擲骰子"], [], [], []

def web_level11(text:str):
    global player_dice, opponent_dice  # 使用全局變量存儲對方的點數
    if text == "換你了":
        opponent_dice = random.randint(1, 6)
        
        if player_dice > opponent_dice:
            return True, [f"我的點數是: {opponent_dice}", "恭喜你贏了！，鑰匙給你，你現在可以去把後門打開了"], [opponent_dice], [], []
        elif player_dice < opponent_dice:
            return True, [f"我的點數是: {opponent_dice}", "很遺憾你輸了！ 遊戲結束Gameover"], [opponent_dice], [], []
        elif player_dice == opponent_dice:
            return False, [f"我的點數是: {opponent_dice}", "平手！我們在比一次吧","輸入'骰子'擲骰子！"], [opponent_dice], [], []
    else:
        return False, ["請輸入 '換你了' 讓對方擲骰子"], [], [], []
