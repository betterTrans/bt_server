from flask import Flask, request, abort
from google.cloud import language_v1 as language
import json

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

if __name__ == "__main__":
  app.run(port=80, debug=True)