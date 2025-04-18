import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import OpenAI

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取 API 金鑰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API Key not found! Please check your .env file.")

# 初始化 OpenAI 客戶端
client = OpenAI()  # ✅ 不需要傳 api_key，它會自動從環境變數讀取

# 預設的系統提示
DEFAULT_PROMPT = """
你是「好搭啦」語音助理，一個為長輩設計的智慧交通導航與協助系統。你的目標是以溫暖、清晰的語氣，引導使用者完成所有導航、求助與訂票操作。

請注意以下重點：
1. 請根據語音內容判斷使用者是否需要：
   - 查詢目的地位置
   - 指引交通路線
   - 安排訂票
   - 緊急聯絡家人
2. 如果提問與導航系統無關，也要以親切的口吻回覆，並引導使用者返回操作流程。
3. 所有回應請簡潔、溫和，避免使用過於專業的術語。
4. 請勿提到你是 AI 或 ChatGPT，而是以「我是您的交通助理」作為開場白。
5. 每次回覆請包含清楚指令建議，例如「我會為您跳轉至購票畫面」、「我會幫您查詢目前站點位置」等。
6. 若可行，請回傳動作意圖，例如：
   - 「動作：navigate to 公路客運＿選客運」
   - 「動作：fill_location from 台北轉運 to 台大癌醫」
"""

def get_assistant_reply(user_query, member_name="liam"):
    """
    取得 OpenAI LLM 回應
    :param user_query: 使用者的問題
    :param member_name: 會員名稱
    :return: AI 回應內容
    """
    # 檢查 member_db.csv 是否存在
    if not os.path.exists("member_db.csv"):
        print("⚠️ member_db.csv 檔案不存在，使用預設提示")
        style_prompt = DEFAULT_PROMPT
    else:
        # 讀取會員資料庫
        try:
            member_df = pd.read_csv("member_db.csv")
            # 確保 CSV 檔案有 "姓名" 和 "偏好" 欄位
            if "姓名" not in member_df.columns or "偏好" not in member_df.columns:
                print("⚠️ member_db.csv 缺少 '姓名' 或 '偏好' 欄位，使用預設提示")
                style_prompt = DEFAULT_PROMPT
            else:
                # 根據 member_name 查找會員資料
                member_info = member_df[member_df["姓名"] == member_name]
                if not member_info.empty:
                    style_prompt = member_info.iloc[0].get("偏好", DEFAULT_PROMPT)
                else:
                    style_prompt = DEFAULT_PROMPT
        except Exception as e:
            print(f"⚠️ 無法讀取 member_db.csv: {e}")
            style_prompt = DEFAULT_PROMPT

    print(f"📝 選擇的提示詞: {style_prompt}")

    # 建立 OpenAI 訊息格式
    messages = [
        {
            "role": "system",  # 修正 role
            "content": style_prompt
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    try:
        # 🎯 高優先度關鍵字指令 - 提前回傳對應指令，避免冗長回應
        keyword_command_map = [
            (["導航", "目的地"], {
                "reply": "為您跳轉到地點搜尋頁面",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "確認地點頁面"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["我要去"], {
                "reply": "正在為您查詢目的地。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "秀出畫面(地址)-1"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["我想去"], {
                "reply": "我會幫您選擇交通工具。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "偏好交通工具選擇step2"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["我要搭公車去", "我要搭捷運去"], {
                "reply": "正在協助您選擇大眾交通工具。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "偏好交通工具選擇step2"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["訂票", "客運", "購票"], {
                "reply": "我會為您跳轉至客運購票頁面。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "公路客運＿選客運"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["求助", "緊急", "聯絡家人"], {
                "reply": "我會幫您聯絡家人。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "分享位置給家人(長者版)"
                },
                "audio_url": "/static/tts_reply.mp3"
            }),
            (["幫我叫車", "計程車", "打車"], {
                "reply": "正在幫您叫車。",
                "command": {
                    "type": "ui",
                    "action": "navigate",
                    "target": "step3-1-1計程車-長輩版"
                },
                "audio_url": "/static/tts_reply.mp3"
            })
        ]

        for keywords, response in keyword_command_map:
            if any(kw in user_query for kw in keywords):
                return response

        # 呼叫 OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",  # 確保使用正確的模型
            messages=messages
        )
        reply_text = completion.choices[0].message.content.strip()

        response = openai.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=reply_text
        )
        with open("static/tts_reply.mp3", "wb") as f:
            f.write(response.content)

        return {
            "reply": reply_text,
            "command": {
                "type": "ui"
            },
            "audio_url": "/static/tts_reply.mp3"
        }
    except Exception as e:
        error_message = f"❌ OpenAI API 發生錯誤: {str(e)}"
        print(error_message)  # 在後端終端機印出錯誤
        return {
            "reply": error_message,
            "command": {
                "type": "ui"
            },
            "audio_url": None
        }
