from flask import Flask, request
# 載入 json 標準函式庫，處理回傳的資料格式
import json
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from config_KEY import line_access_token, line_channel_secret

app = Flask(__name__)


@app.route("/", methods=['POST'])
def linebot():
    msg = ''
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    print(body)
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        imgur_access_token = line_access_token
        secret = line_channel_secret
        # line_bot_api = LineBotApi(imgur_access_token)        # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        msg = json_data['events'][0]['message']['text']      # 取得 LINE 收到的文字訊息
        # tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        with open('data.txt', 'w', encoding='utf-8') as f:
            if msg != '':
                f.write(str(msg))
    except Exception as ex:
        print(ex)
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return msg                                             # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=7414)  # 將端口改為5000