from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import subprocess
import os

# ✅ 正確初始化 Flask
app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)

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

# ✅ 正確綁定 host 和 port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)