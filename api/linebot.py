from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, CarouselColumn,
                            CarouselTemplate, MessageAction, URIAction, ImageCarouselColumn, ImageCarouselTemplate,
                            ImageSendMessage, ButtonsTemplate)
import os
import requests
from bs4 import BeautifulSoup
import random

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def random_ptt_boards():
    board_info = []
    response = requests.get('https://www.ptt.cc/bbs/index.html')
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有討論版的名稱和URL
    data = soup.find_all('div', class_='b-ent')

    for board in data:
        board_name = board.find('div', class_='board-name').text
        board_url = 'https://www.ptt.cc' + board.find('a')['href']
        temp = [board_name, board_url]  # 把板名和 URL 整理成清單
        board_info.append(temp)

    return board_info

def movie_rank(url):
    soup = BeautifulSoup(requests.get(url).text)
    first = soup.find('dl', class_ = 'rank_list_box').find('h2').text
    movie_rank = '第1名：' + first + '\n'

    movie_list = soup.find_all('div', class_ = 'rank_txt')
    for index, info in enumerate(movie_list):
        movie = info.text
        movie_rank += '第{}名：{}\n'.format(str(index + 2), movie)

    return movie_rank

@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # 如果收到訊息是「PTT」就隨機選三個板
    if event.message.text == 'PTT':
        board_info = random_ptt_boards()
        # 從 board_info 裡隨機挑選三個板
        board_list = random.sample(board_info, k=3)

        board_template = TemplateSendMessage(
            alt_text='PTT boards template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://down-tw.img.susercontent.com/file/4968c4b4f185386a219b6396c2698dfc',  # 這裡可以用 PTT 的通用 logo
                        action=URIAction(
                            label=board_list[0][0],  # 第一個板名
                            uri=board_list[0][1]     # 第一個板的 URL
                        )),
                    ImageCarouselColumn(
                        image_url='https://down-tw.img.susercontent.com/file/4968c4b4f185386a219b6396c2698dfc',
                        action=URIAction(
                            label=board_list[1][0],  # 第二個板名
                            uri=board_list[1][1]     # 第二個板的 URL
                        )),
                    ImageCarouselColumn(
                        image_url='https://down-tw.img.susercontent.com/file/4968c4b4f185386a219b6396c2698dfc',
                        action=URIAction(
                            label=board_list[2][0],  # 第三個板名
                            uri=board_list[2][1]     # 第三個板的 URL
                        ))
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, board_template)

    

if __name__ == "__main__":
    app.run()
