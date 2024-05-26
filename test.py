from flask import Flask, Response, render_template
from imgurpython import ImgurClient
import tensorflow as tf
import numpy as np
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


def line_bot_send_msg(situation):
    line_bot_api = LineBotApi(line_access_token)
    if situation == "start":
        messages = [
            TextSendMessage(text='歡迎使用嬰兒照護系統,請提供您的Camera ID'),
        ]
        # 
        line_bot_api.push_message(messages)

def line_bot_send_trigger(image_url, danger_time):
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
    time.sleep(2)
    print("save image to local")

    # 上傳image到Imgur
    client = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)
    image = client.upload_from_path(image_filename , anon=False)
    # 拿取image的url
    image_link = image['link']
    print("upload image to impur")
    return image_link


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
        if b > 0.6: # 影像偵測到危險狀態
            if danger_state is None:
                danger_state = time.time()  # 開始計時
            elif time.time() - danger_state >= 3: # 假設影像處於Danger狀態三秒
                print("Danger!!!!!")
                danger_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒") # 記錄當下發生的時間點
                image_url = impur_get_url(img)
                line_bot_send_msg(image_url, danger_time)
                danger_state = None  # 重設影像狀態
            text = 'Danger!!'
        else:
            danger_state = None  # 重設影像狀態
            if a > 0.6: # 影像偵測到安全狀態
                text = 'ok~'
            else: # 影像偵測到未知狀態
                text = 'Processing...'
        
        cv2.putText(img, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def handle_join(event):
    #---第一步判別使用者輸入camera_id是否正確----------------------------

    # 假設正確的 camera id 為 "abc123"
    valid_camera_id = "abc123"

    msg = json_data['events'][0]['message']['text']
    tk = json_data['events'][0]['replyToken']

    if msg == valid_camera_id:
        reply_text = "歡迎使用,目前已正在監控"
    else:
        reply_text = "請提供正確的 camera id"

    line_bot_api.reply_message(tk, TextSendMessage(text=reply_text))

    #---第二步持續監控影像和回傳trigger訊息---------------------------------

    # 假設觸發事件的相關資訊
    trigger_event = {
        "text": "寶寶被遮掩住口鼻",
        "time": "2023-05-25 15:30:00",
        "location": "辦公室入口",
        "image_url": "https://example.com/trigger.jpg"
    }

    def monitor_camera(event):
        camera_id = event.message.text
        user_id = event.source.user_id

        if camera_id == valid_camera_id:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="歡迎使用,目前已正在監控")
            )
            while True:
                # 模擬持續監控狀態
                print("正在監控中...")
                time.sleep(1)

                # 假設發生觸發事件
                if state == "abnormal":
                    line_bot_api.push_message(
                        user_id,
                        [
                            TextSendMessage(text="Trigger 發生"),
                            TextSendMessage(text=f"Trigger 發生的時間: {trigger_event['time']}"),
                            TextSendMessage(text=f"Trigger 發生的地點: {trigger_event['location']}"),
                            ImageSendMessage(original_content_url=trigger_event['image_url'], preview_image_url=trigger_event['image_url']),
                            TextSendMessage(text="以上情況是否正確?")
                        ]
                    )

                    # 等待使用者回覆
                    user_reply = ""
                    while user_reply.lower() not in ["正確", "不正確"]:
                        message_event = line_bot_api.poll_events()
                        for event in message_event:
                            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
                                user_reply = event.message.text
                                if user_reply.lower() == "正確":
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage(text="是否幫忙撥打 119?")
                                    )
                                    call_119_reply = ""
                                    while call_119_reply.lower() not in ["是", "否"]:
                                        message_event = line_bot_api.poll_events()
                                        for event in message_event:
                                            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
                                                call_119_reply = event.message.text
                                                if call_119_reply.lower() == "是":
                                                    print("正在撥打 119...")
                                                else:
                                                    print("好的,不撥打 119")
                                elif user_reply.lower() == "不正確":
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage(text="是否持續監控?")
                                    )
                                    continue_monitoring_reply = ""
                                    while continue_monitoring_reply.lower() not in ["是", "否"]:
                                        message_event = line_bot_api.poll_events()
                                        for event in message_event:
                                            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
                                                continue_monitoring_reply = event.message.text
                                                if continue_monitoring_reply.lower() == "是":
                                                    continue
                                                else:
                                                    line_bot_api.reply_message(
                                                        event.reply_token,
                                                        TextSendMessage(text="請提供 camera id")
                                                    )
                                                    break
                                else:
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage(text="以上情況是否正確?")
                                    )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請提供正確的 camera id")
                )


        

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    clear_directory("image")
    line_bot_send_msg("start")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)