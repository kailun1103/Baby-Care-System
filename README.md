# Baby Care System

A Flask-based real-time baby monitoring system that uses camera input to detect if a baby’s nose is covered, preventing breathing. Alerts are sent via Line Bot for remote caregiving.


---

## ✨ Features

- **Real-time Video Streaming**  
  Streams live video from a connected camera to a Flask web interface.  
- **Nose-Cover Detection**  
  Uses a pretrained Keras model to detect if the baby’s nose is obstructed.  
- **Instant Alerts via Line Bot**  
  Sends notifications (text and image) to caregivers on LINE when a hazard is detected.  
- **Imgur Integration**  
  Automatically uploads alert snapshots to Imgur and shares the URL in alerts.  
- **Configurable Threshold**  
  Adjust detection sensitivity via a configuration file.

---

## 🛠 Tech Stack

- **Backend:** Flask  
- **ML Model:** TensorFlow / Keras  
- **Computer Vision:** OpenCV  
- **Messaging:** LINE Messaging API (`line-bot-sdk`)  
- **Image Hosting:** Imgur (`imgurpython`)  
- **Data Handling:** NumPy, OpenPyXL  

---

## 🚀 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/kailun1103/Baby-Care-System.git
   cd Baby-Care-System
   ```
2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment**  
   - Rename `config_template.py` to `config.py`.  
   - Edit `config.py` with your LINE channel credentials and Imgur client ID.
4. **Place the Model**  
   Ensure `keras_model.h5` is in the project root.
5. **Run the Application**  
   ```bash
   python app.py
   ```
   Navigate to `http://localhost:5000` in your browser.

---

## ⚙️ Configuration

Edit `config.py` parameters:

```python
LINE_CHANNEL_ACCESS_TOKEN = "<your line token>"
LINE_CHANNEL_SECRET = "<your line secret>"
IMGUR_CLIENT_ID = "<your imgur client id>"
DETECTION_THRESHOLD = 0.5  # Probability threshold for nose-cover alarm
```

---

## 📦 Project Structure

```
.
├── app.py
├── config.py
├── keras_model.h5
├── image/
│   └── monitoring.png
├── templates/
│   └── index.html
├── line_send_msg.py
├── impur_upload_get_url.py
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

1. Fork this repo  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Commit changes (`git commit -m 'Add feature'`)  
4. Push branch (`git push origin feature/YourFeature`)  
5. Open a Pull Request  

Please follow PEP8 guidelines and comment your code.

---

## 🔗 References

1. [Flask Video Streaming by miguelgrinberg](https://github.com/miguelgrinberg/flask-video-streaming)  
2. [Picodet ONNX Runtime Example](https://github.com/hpc203/picodet-onnxruntime)

---

## ✉️ Contact

- **Email:** kailunchang1103@gmail.com  
- **GitHub:** [kailun1103](https://github.com/kailun1103)
