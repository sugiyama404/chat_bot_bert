from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertJapaneseTokenizer, AutoModelForQuestionAnswering

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/', methods=['POST'])
@cross_origin(supports_credentials=True)
def index():
    inp_text = request.form['content']
    rep_text = reply(inp_text)
    print("input:", inp_text)
    print("reply:", rep_text)

    return jsonify({"content": rep_text})


def reply(inp_text):
    context = "本日お昼頃、高崎方面へ自転車で出かけました。"
    # question="どこへ出かけた？"
    question = inp_text
    model = AutoModelForQuestionAnswering.from_pretrained('output/')
    tokenizer = BertJapaneseTokenizer.from_pretrained(
        'cl-tohoku/bert-base-japanese-whole-word-masking')

    inputs = tokenizer.encode_plus(
        question, context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]
    output = model(**inputs)
    answer_start = torch.argmax(output.start_logits)
    answer_end = torch.argmax(output.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(
        tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    return answer


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
