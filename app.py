from flask import Flask, Response, render_template
import cv2
import tensorflow as tf
import numpy as np
import time  # 導入 time 模組來追蹤時間

app = Flask(__name__)

model = tf.keras.models.load_model('keras_model.h5', compile=False)  # 載入模型
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)          # 設定資料陣列

def generate_frames():
    cap = cv2.VideoCapture(0)
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
