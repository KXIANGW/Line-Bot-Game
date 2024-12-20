# Azure Translation
from azure.ai.translation.text import TextTranslationClient
# from azure.ai.translation.text.models import InputTextItem
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Translator Setup
text_translator = TextTranslationClient(
    credential=AzureKeyCredential(config["AzureTranslator"]["Key"]),
    endpoint=config["AzureTranslator"]["EndPoint"],
    region=config["AzureTranslator"]["Region"],
)

"""
翻譯功能
參數為預翻譯內容和翻譯語言
"""
def azure_translate(text: str, target_language: str):
    try:
        # target_languages = ["en", 'ja', 'ko', 'zh-Hans', 'zh-Hant']
        # idx = {'ja':4, "en":4, 'ko':4, 'zh-Hant':index,'zh-Hans':index}
        # from_script = {'ja':'Jpan','zh-Hans':'Hans', 'zh-Hant' : 'Hant' ,'ko':'Kore'}
        # to_script = "Latn"
        # input_text_elements = [InputTextItem(text=user_input)]

        input_text_elements = [text]
        response = text_translator.translate(
            body=input_text_elements, to_language=[target_language]
        )
        print(f"\n{response}\n")
        translation = response[0] if response else None
        return translation.translations[0].text

        detectedLanguage = response[0]['detectedLanguage']['language']
        try:
            response2 = text_translator.transliterate(
                body=[translation.translations[idx[detectedLanguage]].text],
                language=target_languages[idx[detectedLanguage]],
                from_script=from_script[target_languages[idx[detectedLanguage]]],
                to_script=to_script
            )
            transliteration = response2[0] if response else None
            print( transliteration.text, translation.translations[idx[detectedLanguage]].text)
            if transliteration:
                return transliteration.text, translation.translations[idx[detectedLanguage]].text
        except:
            return translation.translations[idx[detectedLanguage]].text, translation.translations[idx[detectedLanguage]].text


    except HttpResponseError as exception:
        print(f"Error Code: {exception.error}")
        print(f"Message: {exception.error.message}")
        return "翻譯錯誤"