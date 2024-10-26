from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import jpholiday
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from linebot import LineBotApi
from linebot.models import TextSendMessage

# .envファイルから環境変数を読み込む
load_dotenv()

# LINE Messaging API設定
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")

def send_line_message(message):
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

def is_day_before_holiday(date):
    weekday = date.weekday()
    next_day = date + timedelta(days=1)
    return weekday == 5 or (weekday == 6 and jpholiday.is_holiday(next_day))

def check_availability():
    url = "https://www3.yadosys.com/reserve/ja/room/calendar/147/ehejfcebejdheigbgihfgpdn/all"

    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendarTable"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        available_dates = []

        calendar_table = soup.find("table", class_="calendarTable")
        if calendar_table:
            rows = calendar_table.find_all("tr")[1:]  # ヘッダー行をスキップ
            for row in rows:
                cells = row.find_all("td")
                for cell in cells:
                    if "dayCell" in cell.get("class", []):
                        date_str = cell.find("div", class_="day").text.strip()
                        if date_str:
                            date = datetime.strptime(f"{datetime.now().year}/{date_str}", "%Y/%m/%d")
                            if is_day_before_holiday(date) and "×" not in cell.text:
                                available_dates.append(date.strftime("%Y-%m-%d"))

        return available_dates
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []
    finally:
        driver.quit()

def main():
    available_dates = check_availability()
    if available_dates:
        message = "ほったらかしキャンプ場で以下の日に空きが出ました:\n" + "\n".join(available_dates)
        send_line_message(message)
    else:
        print("現在、空きはありません。")

if __name__ == "__main__":
    main()