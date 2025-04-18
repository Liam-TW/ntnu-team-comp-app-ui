# vlm_detection.py
import base64
from openai import OpenAI
import os
from dotenv import load_dotenv

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取 API 金鑰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 系統提示
SYSTEM_PROMPT = """
你負責判斷使用者上傳的影像裏頭的人，是否有張開眼睛
如果有張開眼睛，status 設為 true
如果沒有張開眼睛（眼睛是閉上的），status 設為 false

我希望你可以輸出一個 JSON，
裡頭包含 status 和 reason 兩個 key，
如以下範例：
{"status": true, "reason": "請你敘述判斷理由"}

請注意，輸出的時候務必不要包含 ```, `, `json 等字眼，
以免後續無法進行軟體串接。

請你務必輸出
{"status": true, "reason": "請你敘述判斷理由"}
或是
{"status": false, "reason": "請你敘述判斷理由"}
如果無法判斷，那就輸出
{"status": false, "reason": "無法判斷"}
"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_vlm_detection(image_path):
    base64_image = encode_image(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                { "type": "text", "text": SYSTEM_PROMPT },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return completion.choices[0].message.content
