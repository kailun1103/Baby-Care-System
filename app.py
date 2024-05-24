from flask import Flask, Response, render_template, request
from linebot import LineBotApi
from linebot.models import ImageSendMessage
import requests
from imgurpython import ImgurClient
import datetime
import cv2
import tensorflow as tf
import numpy as np
import time  # 導入 time 模組來追蹤時間

import json
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__)

model = tf.keras.models.load_model('keras_model.h5', compile=False)  # 載入模型
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)          # 設定資料陣列

@app.route("/supervise")
def home():
    image_url = request.args.get('param', '預設值')
    line_bot_api = LineBotApi('lHTtqayJe1MN429GbyJjmgrcWbIkUUZ9Rm2pnyHRsZU7mmED1S/dM0FVaqPpXq+uX/G1E3BBfL81xHI66sT+4Hl/DOMjKyVc5u8OwzhnLcznwMXNg1ROe+xrOLHOGsNHuSi94YuaV/lTGx1qP/sE/QdB04t89/1O/w1cDnyilFU=')
    print('------------------------')
    print(image_url)
    print('------------------------')
    try:
        # 指定圖片的原始內容 URL 和預覽圖片 URL
        original_content_url = image_url
        preview_image_url = image_url
        now_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")
        
        # 創建圖片訊息和文字訊息
        messages = [
            ImageSendMessage(
                original_content_url=original_content_url, 
                preview_image_url=preview_image_url
            ),
            TextSendMessage(text='危險啦幹! 觸發Trigger'),
            TextSendMessage(text= now_time),
            TextSendMessage(text='237新北市三峽區大學路151號')
        ]
        
        # 發送多個消息
        line_bot_api.push_message('U4a2b6c651a48061d8408b40b25c03b3c', messages)
        
        print('success')
        return 'OK'
    except Exception as e:
        print('error:', str(e))
        return 'Failed', 500

    

def impur_upload(filename):
    # client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    client = ImgurClient("a0aef3d206a9405", "b5c854b59f60a5daaeb29bf2cb1ada3d00393fe1", "31e29ec2770045828bdf07af121b31fe8a383c6d", "1693d87de9af67966b246a03139c0d6238efeb71")
    # config = {
    #     'album': "kailun1103",
    #     'name': 'test-name!',
    #     'title': 'test-title',
    #     'description': 'test-description'
    # }
    print("Uploading image... ")
    image = client.upload_from_path(filename , anon=False)
    print(image)
    time.sleep(3)
    image_link = image['link']
    print(f"Uploaded image ID: {image_link}")
    return image_link

def trigger(img):

    # 儲存圖片位置
    now = datetime.datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(filename, img)
    print(f"圖像已保存到本地: {filename}")
    time.sleep(5)

    # 上傳圖片，並且拿回url
    image_url = impur_upload(filename)
    return image_url


def generate_frames():
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    danger_start = None  # 記錄首次遇到 Danger!! 的時間

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 左右翻轉影像
        frame = cv2.flip(frame, 1)

        img = cv2.resize(frame, (398, 224))
        img = img[0:224, 80:304]
        image_array = np.asarray(img)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array
        prediction = model.predict(data, verbose=0)  # 禁用進度條
        a, b = prediction[0]
        if b > 0.6:
            if danger_start is None:
                danger_start = time.time()  # 開始計時
            elif time.time() - danger_start >= 3:
                print('trigger')
                image_url = trigger(img)
                requests.get(f'http://127.0.0.1:5000/supervise?param={image_url}')
                # linebot(image_url)
                danger_start = None  # 重設計時器
            text = 'Danger!!'
        else:
            danger_start = None  # 重設計時器
            if a > 0.6:
                text = 'ok~'
            else:
                text = 'Processing...'
        
        cv2.putText(img, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)