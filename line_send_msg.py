from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    print(body)
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        imgur_access_token = '9hPChjfP1nWy3bd+jaoDAsLTV1EzIGfqb4d2YjVb9oke2jCXFWuwTcvcYgF4NU21X/G1E3BBfL81xHI66sT+4Hl/DOMjKyVc5u8OwzhnLcy8PwRjp2qiY61hQqTkan60xyqKI7cm88nMJVkp/uiHugdB04t89/1O/w1cDnyilFU='
        secret = '328c65237339774f75bfd7dc108da0c8'
        line_bot_api = LineBotApi(imgur_access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        msg = json_data['events'][0]['message']['text']      # 取得 LINE 收到的文字訊息
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        # line_bot_api.reply_message(tk,TextSendMessage(msg))  # 回傳訊息
        line_bot_api.reply_message(tk, ImageSendMessage(original_content_url="https://i.imgur.com/6TeK8jB.jpeg", preview_image_url="https://i.imgur.com/wYS9Wdz.jpg"))
        print(msg, tk)   
    except Exception as ex:
        print(ex)
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()