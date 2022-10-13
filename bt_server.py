from flask import Flask, request, abort
from google.cloud import language_v1 as language
import json

import bt_dataset

app = Flask(__name__)

@app.route("/")
def hello():
  return "<h1>「更好的翻譯」隆重登場！</h1>"

@app.route('/api/syntax', methods=['POST'])
def api_syntax():
    data = json.loads(request.values.get("data"))
    sentence = data["sentence"]

    client = language.LanguageServiceClient()

    document = {
            "content": sentence, 
            "type_": language.Document.Type.PLAIN_TEXT, 
            "language": "en" 
        }

    analyze_result = client.analyze_syntax(
            request = {
                'document': document, 
                'encoding_type': language.EncodingType.UTF8
            }
        )
        
    # 20201105: 回應的 analyze_result 似乎已經不是標準的 protobuf message 了，因為無法用 MessageToDict 或 MessageToJson 轉成 JSON
    # 沒辦法的情況下，只好自己建構要送回去的回應。。。
    # 但這樣有可能會遺漏一些陸續新增的屬性，所以另外新增了一個 key-value(AnalyzeSyntaxResponse_to_str)，記錄原始回應（字串形式）
    
    sentences = [
        {
            "text": {
            "content": sent.text.content,
            "beginOffset": sent.text.begin_offset
            }
        }
        for sent in analyze_result.sentences
    ]
    tokens = [
        {
            "text": {
            "content": token.text.content,
            "beginOffset": token.text.begin_offset
            },
            "partOfSpeech": {
            "tag": language.PartOfSpeech.Tag(token.part_of_speech.tag).name,
            "number": language.PartOfSpeech.Number(token.part_of_speech.number).name,
            "mood": language.PartOfSpeech.Mood(token.part_of_speech.mood).name,
            "person": language.PartOfSpeech.Person(token.part_of_speech.person).name,
            "tense": language.PartOfSpeech.Tense(token.part_of_speech.tense).name
            },
            "dependencyEdge": {
            "headTokenIndex": token.dependency_edge.head_token_index,
            "label": language.DependencyEdge.Label(token.dependency_edge.label).name
            },
            "lemma": token.lemma
        }
        for token in analyze_result.tokens
    ]
    my_analyze_result = {
        "sentences": sentences,
        "tokens": tokens,
        "language": analyze_result.language,
        "AnalyzeSyntaxResponse_to_str": str(analyze_result)
    }


    analyze_result_json = json.dumps(my_analyze_result)

    return analyze_result_json

@app.route('/api/save_term', methods=['POST'])
def api_save_term():
    try:
        data = json.loads(request.values.get("data"))

        record_to_save = data['form_input']
        if (record_to_save['ot_text'] and record_to_save['tt_text']): # 至少【原文】【人譯】這兩個欄位一定要有值
            return_str = bt_dataset.saveTerm(record_to_save)
            return json.dumps({
                'action': 'save',
                'type': 'term',
                'return_str': return_str,
            });
        else:
            raise
    except:
        return_str = 'save_term 出問題了。。。'
        abort(404, return_str)

@app.route('/api/delete_term', methods=['POST'])
def api_delete_term():
    try:
        data = json.loads(request.values.get("data"))

        record_to_delete = data['form_input']
        if (record_to_delete['ot_text'] and record_to_delete['tt_text']): # 至少【原文】【人譯】這兩個欄位一定要有值
            return_str = bt_dataset.deleteTerm(record_to_delete)
            return json.dumps({
                'action': 'save',
                'type': 'term',
                'return_str': return_str,
            });
        else:
            raise
    except:
        return_str = 'delete_term 出問題了。。。'
        abort(404, return_str)

@app.route('/api/get_terms', methods=['POST'])
def api_get_terms():
    try:
        data = json.loads(request.values.get("data"))

        tokens = data["tokens"]
        if (tokens):
            saved_terms = bt_dataset.getTerms(tokens)
            return json.dumps({
                'action': 'get',
                'type': 'terms',
                'return_str': 'get_terms 已順利取得資料。',
                'saved_terms': saved_terms,
            });
        else:
            raise
    except:
        return_str = 'get_terms 出問題了。。。'
        abort(404, return_str)

if __name__ == "__main__":
  app.run(port=80, debug=True)