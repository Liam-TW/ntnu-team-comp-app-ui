import os
from dotenv import load_dotenv

# 手動指定 .env 路徑
dotenv_path = "/Users/liam/Desktop/NTNU/AI_NTNU/.env"
load_dotenv(dotenv_path)

# 嘗試讀取 API Key
api_key = os.getenv("OPENAI_API_KEY")

print(f"API Key: {api_key}")  # 應該要顯示 API Key，否則 .env 沒有正確載入