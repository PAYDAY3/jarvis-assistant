from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime

app = Flask(__name__)

# 初始化语音识别器
recognizer = sr.Recognizer()

# 初始化文本到语音引擎
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('voice', 'zh')

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="zh-CN")
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Could not request results"}), 500

@app.route('/respond', methods=['POST'])
def respond():
    data = request.json
    text = data.get('text', '')
    
    response = process_command(text)
    
    # 将响应转换为语音
    engine.save_to_file(response, 'response.mp3')
    engine.runAndWait()
    
    return jsonify({"response": response, "audio": "response.mp3"})

def process_command(text):
    text = text.lower()
    if "你好" in text or "嗨" in text:
        return "你好！我是Jarvis，有什么我可以帮你的吗？"
    elif "时间" in text:
        current_time = datetime.datetime.now().strftime("%H:%M")
        return f"现在的时间是 {current_time}"
    elif "天气" in text:
        return "抱歉，我目前无法获取实时天气数据。"
    else:
        return "抱歉，我没有理解这个命令。你能换个方式问或者问点别的吗？"

if __name__ == '__main__':
    app.run(debug=True)

