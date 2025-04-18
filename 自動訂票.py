from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://order.kingbus.com.tw/ORD/ORD_M_1510_OrderGo.aspx")

# 填入基本資料
driver.find_element("id", "ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys("A123456789")
driver.find_element("id", "ctl00_ContentPlaceHolder1_txtPhone").send_keys("0912345678")
driver.find_element("id", "ctl00_ContentPlaceHolder1_txtCustomer_N").send_keys("王大明")

# 點下一步
driver.find_element("id", "ctl00_ContentPlaceHolder1_btnStep1_OK").click()
time.sleep(3)  # ⏳ 等畫面跳轉

# 填寫起站
from_select = Select(driver.find_element("id", "ctl00_ContentPlaceHolder1_ddlStation_ID_From"))
from_select.select_by_visible_text("台北轉運")

# 等待訖站選單變更（監測 option 數量變化）
WebDriverWait(driver, 10).until(
    lambda d: "高雄中正" in [opt.text.strip().replace('　', '') for opt in Select(d.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlStation_ID_To")).options]
)

# 填寫迄站（等待載入後再選）
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ddlStation_ID_To"))
)

WebDriverWait(driver, 10).until(
    lambda d: len(Select(d.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlStation_ID_To")).options) > 10
)

# 為避免 stale element，重抓一次 select 物件
to_select_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlStation_ID_To")
to_select = Select(to_select_element)

found = False
for option in to_select.options:
    text = option.text.strip().replace('　', '')
    print(f"🔍 選項值: {option.get_attribute('value')} / 顯示文字: '{text}'")
    if text == "高雄中正":
        option.click()
        found = True
        break

if not found:
    print("⚠️ 未找到 '高雄中正' 目的地")

# 日期
try:
    date_input = driver.find_element("id", "ctl00_ContentPlaceHolder1_txtOut_Dt")
    date_input.clear()
    today = datetime.today().strftime("%Y/%m/%d")
    date_input.send_keys(today)
except Exception as e:
    print("❌ 日期填寫失敗：", e)

# 填寫時間
Select(driver.find_element("id", "ctl00_ContentPlaceHolder1_ddlHour")).select_by_visible_text("18")
time.sleep(0.5)

# 等待分鐘選單載入與可點擊
try:
    min_select_elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ddlMin"))
    )
    Select(min_select_elem).select_by_visible_text("00")
except Exception as e:
    print("❌ 無法選取分鐘選單：", e)

# 點下一步
try:
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnStep2_OK"))
    )
    time.sleep(0.5)  # 保險性等待
    next_btn.click()
    print("✅ 成功點擊下一步")
except Exception as e:
    print("❌ 無法點擊下一步按鈕：", e)

