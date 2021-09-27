from typing import Counter
from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertJapaneseTokenizer, AutoModelForQuestionAnswering
import random


app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/', methods=['POST'])
@cross_origin(supports_credentials=True)
def index():
    empty_flag = True
    inp_text = request.form['content']
    rep_text = reply(inp_text)
    doc = txt_to_list()
    if rep_text != '':
        rep = transform_charactor(rep_text)
        doc.insert(0, rep)
        empty_flag = False

    mg_txt = inp_text + rep_text
    rep_text = similar_document_search(mg_txt, doc, empty_flag)
    print("input:", inp_text)
    print("reply:", rep_text)

    return jsonify({"content": rep_text})


def reply(inp_text):
    context = get_context()

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
    answer = answer.replace(' ', '')
    return answer


def similar_document_search(cand, refs, empty_flag):

    def calc_bert_score(cands, refs):
        from bert_score import score

        Precision, Recall, F1 = score(cands, refs, lang="ja", verbose=False)
        return F1.numpy().tolist()

    cands = []
    for i in refs:
        cands.append(cand)

    f1 = calc_bert_score(cands, refs)
    data = []
    for item, ref in zip(f1, refs):
        data.append([item, ref])
    data.sort(reverse=True)

    f_flag = True
    counter = 0
    f_num = 0.0
    data2 = []
    for it, it2 in data:
        if (f_num > it) or (counter > 5):
            break

        if f_flag:
            f_num = it
            f_num = f_num - 0.05
            f_flag = False

        print(it, ' ', it2)
        data2.append([it, it2])
        counter += 1

    str = ''
    if (len(data2) >= 2):
        num = random.randrange(len(data2))
        str = data2[num][1]

    else:
        str = data2[0][1]

    return str


def get_context():
    with open('context/me.txt') as f:
        s = f.read()
    s = s.replace('\n', '')
    return s


def transform_charactor(rep_text):
    rep = ''
    rep = rep_text + 'だよ！！'
    return rep


def txt_to_list():
    doc = []
    fileobj = open("context/dailogue.txt", "r", encoding="utf_8")
    while True:
        line = fileobj.readline()
        if line and (line.strip() != ''):
            # line には行末の改行コードまで含まれてる
            doc.append(line.strip())
        else:
            break
    return doc


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
