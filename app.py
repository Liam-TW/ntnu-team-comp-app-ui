from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-ticket', methods=['POST'])
def run_ticket():
    try:
        # 呼叫 Selenium 腳本，例如：自動填寫訂票表單
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

if __name__ == '__main__':
    app.run(debug=True)