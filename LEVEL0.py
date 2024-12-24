import configparser
import wave
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason
from module.azure import azure_translate

# Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

def azure_speech(target_language):
    # 獲取 Azure Speech 的 Key, Region
    speech_key = config["AzureSpeech"]["SPEECH_KEY"]
    service_region = config["AzureSpeech"]["SPEECH_REGION"]
    
    # 初始化 Speech 配置
    speech_config = SpeechConfig(subscription=speech_key, region=service_region)

    # 設定輸出檔案
    file_name = "outputaudio.wav"
    file_path = "static/" + file_name
    file_config = AudioConfig(filename=file_path)

    voice_map = {
    "en": {"lang": "en-US", "voice": "en-US-GuyNeural"},           # 英文
    "zh-Hant": {"lang": "zh-CN", "voice": "zh-CN-YunyangNeural"},  # 中文繁體
    "zh-Hans": {"lang": "zh-CN", "voice": "zh-CN-YunyangNeural"},  # 中文簡體
    "ja": {"lang": "ja-JP", "voice": "ja-JP-NaokiNeural"},         # 日文
    "ko": {"lang": "ko-KR", "voice": "ko-KR-InJoonNeural"},        # 韓文
    }

    # 設置對應的語音配置
    if target_language in voice_map:
        selected_voice = voice_map[target_language]
        speech_config.speech_synthesis_voice_name = selected_voice["voice"]

    user_input = "大家好，我是旭東爸爸，最近有很多學生向我反應想打開後門，那我就大發慈悲給大家一個機會，如果順利通關，我就讓你們開"
    translated_text = azure_translate(text=user_input, target_language=target_language)
    print(translated_text)
    # 使用 SSML 調整語速與音調
    # 提取字典的值
    lang = selected_voice["lang"]
    voice_name = selected_voice["voice"]

    # 使用 .format 動態生成 SSML
    user_input = """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
        xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{lang}">
        <voice name="{voice_name}">
            <prosody rate="-20%" pitch="-7%">
                {translated_text}
            </prosody>
        </voice>
    </speak>
    """.format(lang=lang, voice_name=voice_name, translated_text=translated_text)

    # 初始化語音合成器
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    # 語音合成
    result = synthesizer.speak_ssml_async(user_input).get()

    # 檢查生成結果
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        print(f"語音合成成功，文件保存至: {file_path}")
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"語音合成被取消: {cancellation_details.reason}")
        if cancellation_details.error_details:
            print(f"錯誤: {cancellation_details.error_details}")
        return None

    # 計算音檔時長
    try:
        with wave.open(file_path, 'r') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = round(frames / float(rate) * 1000) 
            print(f"音檔時長: {duration:.2f} 秒")
            return duration
    except Exception as e:
        print(f"無法計算時長: {e}")
        return None