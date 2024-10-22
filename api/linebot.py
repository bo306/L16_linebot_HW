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

def ptt_subcategories(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    subcategories = []

    # 抓取子分類的名稱和連結
    data = soup.find_all('div', class_='b-ent')
    for item in data:
        category_name = item.find('div', class_='board-name').text
        category_url = 'https://www.ptt.cc' + item.find('a')['href']
        subcategories.append([category_name, category_url])

    return subcategories
  
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
                        image_url='https://down-tw.img.susercontent.com/file/4968c4b4f185386a219b6396c2698dfc@resize_w900_nl.webp',  # 這裡可以用 PTT 的通用 logo
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

    if event.message.text == '分類':
    button_template = TemplateSendMessage(
        alt_text='button template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/a5MK3cu.jpeg',
            title='PTT 生活娛樂類分類',
            text='請選擇要查看的分類',
            actions=[
                MessageAction(
                    label='查看分類',
                    text='查看分類'
                )
            ])
        )
    line_bot_api.reply_message(event.reply_token, button_template)

if event.message.text == '查看分類':
    # 抓取 PTT 生活娛樂類的子分類
    subcategories = ptt_subcategories('https://www.ptt.cc/cls/1')

    # 顯示前 3 個分類作為範例（你可以顯示更多或使用 ImageCarouselTemplate 顯示）
    category_template = TemplateSendMessage(
        alt_text='category template',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://www.ptt.cc/images/logo.png',
                    action=URIAction(
                        label=subcategories[0][0],  # 第 1 個子分類的名稱
                        uri=subcategories[0][1]    # 第 1 個子分類的 URL
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://www.ptt.cc/images/logo.png',
                    action=URIAction(
                        label=subcategories[1][0],  # 第 2 個子分類的名稱
                        uri=subcategories[1][1]    # 第 2 個子分類的 URL
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://www.ptt.cc/images/logo.png',
                    action=URIAction(
                        label=subcategories[2][0],  # 第 3 個子分類的名稱
                        uri=subcategories[2][1]    # 第 3 個子分類的 URL
                    )
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, category_template)

if __name__ == "__main__":
    app.run()
