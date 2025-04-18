from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_cors import CORS
import subprocess
import os
import openai
from dotenv import load_dotenv
from llm_response import get_assistant_reply
load_dotenv()

# ✅ 正確初始化 Flask
app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 提供 static 路由給 mp3 播放使用
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# ✅ 設定圖片路由，從 images 資料夾讀取
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

# ✅ 首頁 index
@app.route('/')
def index():
    return render_template('index.html')

# ✅ 自動訂票的後端 API
@app.route('/run-ticket', methods=['POST'])
def run_ticket():
    try:
        result = subprocess.run(
            ['python3', '自動訂票.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return jsonify({"status": "success", "message": result.stdout})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/ai-assistant", methods=["POST"])
def ai_assistant():
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"reply": "未收到語音內容"})

    try:
        # 清空舊的語音檔案
        for file in os.listdir("static"):
            if file.endswith(".mp3"):
                os.remove(os.path.join("static", file))

        result = get_assistant_reply(query)
        reply = result.get("reply", "")
        audio_path = result.get("audio_path", "")

        response_data = {"reply": reply, "audio_url": "/static/tts_reply.mp3"}  # 將前端可播放路徑改為 audio_url 命名
        if audio_path:
            filename = os.path.basename(audio_path)
            response_data["audio_url"] = f"/static/{filename}"

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"reply": f"發生錯誤：{str(e)}"})

# ✅ 正確綁定 host 和 port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)