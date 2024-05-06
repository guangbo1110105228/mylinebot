from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
#======python的函數庫==========


import json

app = Flask(__name__)
# LINE BOT info
line_bot_api = LineBotApi('Channel Access Token')
handler = WebhookHandler('Channel Secret')
openai.api_key = ('YOUR_OPENAI_API_KEY')


def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer

def handle_follow(event):
    user_id = event.source.user_id

    # Send three JSON files to the user
    with open('tofel.json', 'r', encoding='utf-8') as file:
        content1 = json.load(file)
    with open('bigexam.json', 'r', encoding='utf-8') as file:
        content2 = json.load(file)
    with open('ielts.json', 'r', encoding='utf-8') as file:
        content3 = json.load(file)

    line_bot_api.push_message(user_id, [
        FlexSendMessage(alt_text="File 1", contents=content1),
        FlexSendMessage(alt_text="File 2", contents=content2),
        FlexSendMessage(alt_text="File 3", contents=content3)
    ])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text

    try:
        if message == 'HI':
            with open('tofel.json', 'r', encoding='utf-8') as file:
                FlexMessage = json.load(file)
            line_bot_api.reply_message(reply_token, FlexSendMessage('Profile Card', FlexMessage))
        else:
            GPT_answer = GPT_response(message)
            line_bot_api.reply_message(reply_token, TextSendMessage(text=GPT_answer))
    except Exception as e:
        print(traceback.format_exc())
        line_bot_api.reply_message(reply_token, TextSendMessage('An error occurred, please check the logs for more details.'))



import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)