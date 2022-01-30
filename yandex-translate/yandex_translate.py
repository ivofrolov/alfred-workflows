import os, urllib2, json

API_URL = 'https://translate.api.cloud.yandex.net/translate/v2/translate'

def get_translated(text, to, fr=None):
    request = urllib2.Request(API_URL)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Authorization', 'Api-Key %s' % os.getenv('YANDEX_TRANSLATE_API_KEY'))
    request.add_data(json.dumps({
        'sourceLanguageCode': fr,
        'targetLanguageCode': to,
        'texts': [ text, ]
    }))
    response = urllib2.urlopen(request)
    return json.load(response)['translations'][0]['text']

def translate(original_text, to, fr=None):
    translated_text = get_translated(original_text, to, fr)
    result = {'items': [{
        'title': translated_text,
        'arg': original_text,
        'text': {'copy': translated_text, 'largetype': translated_text}
    }]}
    return json.dumps(result)
