import json
from datetime import datetime
import os, shutil

class User:
    def __init__(self, userID: str = "", lang: str = "zh-Hant", level: int = 0, HP: int=3, card=False, state=False, timestamp: str = ""):
        """
        userID: 使用者 ID
        lang: 語言
        level: 目前到達哪一關卡
        HP: 血條(預設3)
        card: 命運卡
        state: 紀錄是否有使用命運卡
        timestamp: 儲存更新時間
        """
        self.userID = userID
        self.lang = lang
        self.level = level
        self.HP = HP
        self.card = card
        self.state = state
        self.timestamp = timestamp
    
    def __str__(self):
        # 使用 vars() 或 self.__dict__ 獲取所有成員變數
        # User({'userID': '', 'lang': 'zh-Hant', 'level': 0, 'timestamp': ''})
        return f"{self.__class__.__name__}({vars(self)})"
    
    # 將 User 物件轉換為字典，方便 JSON 存取
    def to_dict(self):
        return {
            "lang": self.lang,
            "level": self.level,
            "HP": self.HP,
            "card": self.card,
            "state": self.state,
            "timestamp": self.timestamp
        }

    '''
    class method
    將型態轉 User類別(回傳物件)
    '''
    @classmethod
    def from_dict(cls, userID: str, data: dict):
        return cls(userID=userID, lang=data.get("lang", "zh-Hant"), level=data.get("level", 0), HP=data.get("HP", 3), timestamp=data.get("timestamp", ""))


class UserDataManager:
    def __init__(self, folder_path: str):
        '''
        __folder_path: 讀檔寫檔的資料夾路徑
        __user_data_path: 讀寫檔案路徑
        __user_data: {userID: User} 存放所有使用者的資料，以 UserID 搭配 User 類別物件
        '''
        self.__folder_path = folder_path
        os.makedirs(folder_path, exist_ok=True)
        self.__user_data_path = os.path.join(self.__folder_path, "user_data.json")

        self.__user_data = self.__load_json()

    def __load_json(self):
        try:
            with open(self.__user_data_path, 'r', encoding='utf-8') as inFile:
                rawData = json.load(inFile)
                return {userID: User.from_dict(userID, data) for userID, data in rawData.items()}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def __save_json(self):
        with open(self.__user_data_path, 'w', encoding='utf-8') as outFile:
            json.dump({userID: user.to_dict() for userID, user in self.__user_data.items()},
                      outFile, 
                      indent=4,              # indent 排版
                      ensure_ascii=False)  
            
    def save(self, user: User):
        user.timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.__user_data[user.userID] = user
        print(f"Saved {user.userID} successfully!\n")
        self.__save_json()

    def add_or_update_user(self, user: User):
        user.timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.__user_data[user.userID] = user
        self.__save_json()
        self.__create_user_folder(user.userID)
        print(f"Added {user.userID} successfully!\n")

    # def set_level(self, userID: str, level: int):
    #     self.__user_data[userID]["level"] = level
    #     self.__save_json()

    # def set_lang(self, userID: str, lang: str):
    #     self.__user_data[userID]["lang"] = lang
    #     self.__save_json()

    def get_user_data(self, userID: int):
        return self.__user_data.get(userID, None)
    
    
    def get_all_users(self):
        return self.__user_data

    def delete_user(self, identifier):
        if isinstance(identifier, str):
            if identifier in self.__user_data:
                self.__remove_user_folder(userID=identifier)
                del self.__user_data[identifier]
                self.__save_json()
                print(f"Deleted {identifier} successfully!\n")
        elif isinstance(identifier, User):
            if identifier.userID in self.__user_data:
                self.__remove_user_folder(userID=identifier.userID)
                del self.__user_data[identifier.userID]
                self.__save_json()
                print(f"Deleted {identifier.userID} successfully!\n")

    def __create_user_folder(self, userID: str):
        folder_path = os.path.join(self.__folder_path, userID)
        os.makedirs(folder_path, exist_ok=True)

    def __remove_user_folder(self, userID: str):
        folder_path = os.path.join(self.__folder_path, userID)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"{folder_path} is removed")
        else:
            print(f"{folder_path} is not exist")

    def save_image(self, user: User, image):
        file_path = f'{self.__folder_path}/{user.userID}/{user.level}.jpg'
        with open(file_path, 'wb') as inFile:
            inFile.write(image)

        print(f'Image saved at {file_path}')
        return file_path


    

