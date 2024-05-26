from flask import Flask, Response, render_template
from imgurpython import ImgurClient
import tensorflow as tf
import numpy as np
import threading
import datetime
import shutil
import time
import cv2
import os

from config_KEY import imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token, line_access_token, line_user_id

from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage


app = Flask(__name__)

model = tf.keras.models.load_model('keras_model.h5', compile=False)  # 載入模型
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)          # 設定資料陣列


# 刪除目錄底下的所有文件(圖片)
def clear_directory(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) 
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def line_bot_send_msg(image_url, danger_time):
    line_bot_api = LineBotApi(line_access_token)
    try:
        # 指定圖片的原始內容 URL 和預覽圖片 URL
        original_content_url = image_url
        preview_image_url = image_url
        messages = [
            ImageSendMessage(
                original_content_url=original_content_url, 
                preview_image_url=preview_image_url
            ),
            TextSendMessage(text='危險啦幹! 觸發Trigger'),
            TextSendMessage(text= danger_time),
            TextSendMessage(text='237新北市三峽區大學路151號')
        ]
        # 發送多個消息
        line_bot_api.push_message(line_user_id, messages)
        print("sent msg from line bot")
        return 'OK'
    except Exception as ex:
        print('error:', str(ex))
        return 'Failed', 500


def impur_get_url(img):
    # 先儲存image到本地端
    image_filename = datetime.datetime.now().strftime("image/%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(image_filename, img)
    print("save image to local")

    # 上傳image到Imgur
    client = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)
    image = client.upload_from_path(image_filename , anon=False)
    # 拿取image的url
    image_link = image['link']
    print("upload image to impur")
    return image_link


def upload_and_send(img, danger_time):
    image_url = impur_get_url(img)
    line_bot_send_msg(image_url, danger_time)


def generate_frames():
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
    danger_state = None  # 記錄是否遇到 Danger
    
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1) # 左右翻轉影像
        if not ret:
            break
        img = cv2.resize(frame, (398, 224))
        img = img[0:224, 80:304]
        image_array = np.asarray(img)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array
        prediction = model.predict(data, verbose=0)

        # a表示模型預測出正常安全情況的概率或置信度
        # b表示模型預測出某種危險情況的概率或置信度
        a, b = prediction[0]
        if b > 0.6:
            if danger_state is None:
                danger_state = time.time()
            elif time.time() - danger_state >= 3:
                print("Danger!!!!!")
                danger_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")
                # 在新的執行緒中執行上傳和發送訊息的任務
                t = threading.Thread(target=upload_and_send, args=(img, danger_time))
                t.start()
                danger_state = None
            text = 'Danger!!'
        else:
            danger_state = None
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
    clear_directory("image")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)