import config
import requests

traducao = config.keys['yandex']

idiomas = [
    'az', 'ml', 'sq',  'mt', 'am',  'mk', 'en',  'mi', 'ar', 'mr', 'hy', 'mhr', 'af', 'mn', 'eu', 'de', 'ba',  'ne', 'be',
    'no', 'bn', 'pa',  'my', 'pap', 'bg', 'fa',  'bs', 'pl', 'cy', 'pt', 'hu',  'ro', 'vi', 'ru', 'ht', 'ceb', 'gl', 'sr',
    'nl', 'si', 'mrj', 'sk', 'el',  'sl', 'ka',  'sw', 'gu', 'su', 'da', 'tg',  'he', 'th', 'yi', 'tl', 'id',  'ta', 'ga',
    'tt', 'it', 'te',  'is', 'tr',  'es', 'udm', 'kk', 'uz', 'kn', 'uk', 'ca',  'ur', 'ky', 'fi', 'zh', 'fr',  'ko', 'hi',
    'xh', 'hr', 'km',  'cs', 'lo',  'sv', 'la',  'gd', 'lv', 'et', 'lt', 'eo',  'lb', 'jv', 'mg', 'ja', 'ms'
]


def obter_idioma(text):
    if len(text.split()) > 0:
        lang = text.split()[0]
        if lang.split('-')[0] not in idiomas:
            lang = 'pt'
        if len(lang.split('-')) > 1:
            if lang.split('-')[1] not in idiomas:
                lang = 'pt'
    else:
        lang = 'pt'
    return lang


def traduzir(message,client):
    if message.text.startswith('/tr ') or message.text == '/tr':
        text = message.text[4:]
        lang = obter_idioma(text)
        try:
            text = message.reply_to_message.text
        except:
            text = text.replace(lang, '', 1).strip() if text.startswith(lang) else text
        if len(text) > 0:
            sent = client.send_message(message.chat.id, 'Traduzindo...',reply_to_message_id=message.message_id)
            req = requests.post("https://translate.yandex.net/api/v1.5/tr.json/translate",
                data=dict(key=traducao, lang=lang, text=text)).json()
            client.edit_message_text(message.chat.id, sent.message_id,
                                    '''<b>Idioma:</b> {}
<b>Tradução:</b> <code>{}</code>'''.format(req['lang'], req['text'][0]),parse_mode='HTML')
        else:
            client.sendMessage(message.chat.id, 'Uso: /tr <idioma> texto para traduzir (pode ser usado em resposta a uma mensagem).',reply_to_message_id=message.message_id)
