from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import json
import openai
import traceback
import logging
import os

# 設置日誌
logging.basicConfig(level=logging.INFO)

# LINE BOT info
line_bot_api = LineBotApi('kWEiBIJ2Wmv6+ork0tozb2A1v49HfxQxeLbmQZK3lNB/YYmHJ21AR8CO+BUMFc5n+wAKih8OjUnLVQAyk//4ilJie0vAadlRwHg2xEVyrxl+Hxh+ujzf3FwbBvQ96m2YCVK0t7KSKJjtB/HPPxza/AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c0a0777fc50718d93cb976c2cb83a5e3')
openai.api_key = ('sk-proj-W7y6ruWPwwALgjkqpvi9T3BlbkFJar36bApbgvH9lijGGtQa')

app = Flask(__name__)

def GPT_response(text):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=500
        )
        answer = response['choices'][0]['text'].replace('。','')
        return answer
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return "An error occurred while generating the response."

def handle_follow(event):
    user_id = event.source.user_id

    # Send three JSON files to the user
    try:
        with open('../tofel.json', 'r', encoding='utf-8') as file:
            content1 = json.load(file)
        with open('../bigexam.json', 'r', encoding='utf-8') as file:
            content2 = json.load(file)
        with open('../ielts.json', 'r', encoding='utf-8') as file:
            content3 = json.load(file)

        line_bot_api.push_message(user_id, [
            FlexSendMessage(alt_text="File 1", contents=content1),
            FlexSendMessage(alt_text="File 2", contents=content2),
            FlexSendMessage(alt_text="File 3", contents=content3)
        ])
    except Exception as e:
        logging.error(f"Error in handle_follow: {traceback.format_exc()}")
        line_bot_api.push_message(user_id, TextSendMessage('An error occurred while sending files.'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: %s", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        app.logger.error(f"Exception: {e}")
    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
    reply_token = event.reply_token
    message = event.message.text
    app.logger.info(f"Received message: {message}")

    try:
        if message == 'HI':
            with open('../tofel.json', 'r', encoding='utf-8') as file:
                FlexMessage = json.load(file)
            line_bot_api.reply_message(reply_token, FlexSendMessage('Profile Card', FlexMessage))
        else:
            GPT_answer = GPT_response(message)
            line_bot_api.reply_message(reply_token, TextSendMessage(text=GPT_answer))
    except Exception as e:
        app.logger.error(f"Error: {traceback.format_exc()}")
        line_bot_api.reply_message(reply_token, TextSendMessage('An error occurred, please check the logs for more details.'))

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(event)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)





