import configparser
import wave
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason
from module.azure import azure_translate

# Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

def azure_speech(user_input, target_language, voiceName, fileOrder):
    # 獲取 Azure Speech 的 Key, Region
    speech_key = config["AzureSpeech"]["SPEECH_KEY"]
    service_region = config["AzureSpeech"]["SPEECH_REGION"]
        
    # 初始化 Speech 配置
    speech_config = SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voiceName
    
    # 設置輸出文件
    file_name = ".wav"
    file_path = "static/outputaudio_" + fileOrder + file_name
    file_config = AudioConfig(filename=file_path)

    translated_text = azure_translate(text=user_input, target_language=target_language)
    print(translated_text)

    # 初始化語音合成器
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    # 語音合成
    result = synthesizer.speak_text_async(translated_text).get()
    
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
            return file_path, duration
    except Exception as e:
        print(f"無法計算時長: {e}")
        return None