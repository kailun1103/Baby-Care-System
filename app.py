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


line_msg = ""
trigger = None


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


def line_bot_send_msg(image_url, danger_time, state):
    line_bot_api = LineBotApi(line_access_token)
    if state == "safe":
        msg_text = '監測安全'
    else:
        msg_text = '危險啦幹! 觸發Trigger'

    try:
        # 指定圖片的原始內容 URL 和預覽圖片 URL
        original_content_url = image_url
        preview_image_url = image_url
        messages = [
            ImageSendMessage(
                original_content_url=original_content_url, 
                preview_image_url=preview_image_url
            ),
            TextSendMessage(text= msg_text),
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


def upload_and_send(img, danger_time, state):
    image_url = impur_get_url(img)
    line_bot_send_msg(image_url, danger_time, state)


def check_danger_state():
    print('not trigger')
    global trigger
    trigger = True
    time.sleep(6)
    line_bot_api = LineBotApi(line_access_token)
    # messages = [
    #     TextSendMessage(text='是否有接收到訊息?(有的話請回答"是")'),
    # ]
    # line_bot_api.push_message(line_user_id,messages)
    previous_msg = "None"  # 初始化為None

    while True:
        if line_msg == "是":
            messages = [
                TextSendMessage(text='本系統將持續監控嬰兒'),
            ]
            line_bot_api.push_message(line_user_id,messages)
            trigger = None
            with open('data.txt', 'w', encoding='utf-8') as f:
                f.write(str(""))
            break
        else:
            if line_msg != previous_msg:  # 檢查line_msg是否與前一次迴圈不同
                print(line_msg)
                print(previous_msg)
                previous_msg = line_msg  # 更新previous_msg為當前的line_msg值
                messages = [
                    TextSendMessage(text='是否有接收到訊息?(有的話請回答"是")'),
                ]
                line_bot_api.push_message(line_user_id,messages)



def generate_frames():
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
    danger_state = None  # 記錄是否遇到 Danger

    timer = time.time()
    safe_trigger = False
    global trigger
    
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

        real_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")

        # a表示模型預測出正常安全情況的概率或置信度
        # b表示模型預測出某種危險情況的概率或置信度

        if trigger == None:
            print('trigger')
            if time.time() - timer >= 30:
                safe_trigger = True

            a, b = prediction[0]
            if b > 0.6:
                if danger_state is None:
                    danger_state = time.time()
                elif time.time() - danger_state >= 3:
                    print("Danger!!!!!")
                    
                    # 在新的執行緒中執行上傳和發送訊息的任務
                    t = threading.Thread(target=upload_and_send, args=(img, real_time, "Danger"))
                    t.start()
                    n = threading.Thread(target=check_danger_state)
                    n.start()
                    danger_state = None
                    safe_trigger = False
                    timer = time.time()
                text = 'Danger!!'
            else:
                danger_state = None
                if a > 0.6:
                    if safe_trigger == True:
                        print("觸發監控功能")
                        z = threading.Thread(target=upload_and_send, args=(img, real_time, "safe"))
                        z.start()
                        safe_trigger = False
                        timer = time.time()

                    text = 'ok~'
                else:
                    text = 'Processing...'
        else:
            continue

        cv2.putText(img, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        

def check_camera_id():

    line_bot_api = LineBotApi(line_access_token)
    messages = [
        TextSendMessage(text='歡迎使用嬰兒照護系統,請提供您的Camera ID'),
    ]
    line_bot_api.push_message(line_user_id,messages)

    valid_camera_id = "abc123"
    previous_msg = "None"  # 初始化為None

    while True:
        if valid_camera_id == line_msg:
            messages = [
                TextSendMessage(text='歡迎使用baby care system，本系統將會即時監控嬰兒'),
            ]
            line_bot_api.push_message(line_user_id,messages)
            break
        else:
            if line_msg != previous_msg:  # 檢查line_msg是否與前一次迴圈不同
                previous_msg = line_msg  # 更新previous_msg為當前的line_msg值
                messages = [
                    TextSendMessage(text='請提供正確id'),
                ]
                line_bot_api.push_message(line_user_id,messages)
    


def line_reeltime_msg():
    global line_msg
    while True:
        with open('data.txt', 'r', encoding='utf-8') as f:
            line_msg = f.read()
        

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    with open('data.txt', 'w', encoding='utf-8') as f:
        f.write(str(""))
    t = threading.Thread(target=line_reeltime_msg)
    t.start()
    clear_directory("image")
    # check_camera_id()
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)