import time
from datetime import datetime, timedelta
import calendar
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from linebot import LineBotApi
from linebot.models import TextSendMessage

# LINE Messaging API設定
CHANNEL_ACCESS_TOKEN = "dxkyN6fQS0Ewy+/5vzlusIT+D3rLCCFJH6fl4TcSeLWdSgv7BSmuqrWmvvccTCYMVugZ6+xJE5NJkMn7SIcZQdyEfClGJtqgIaHlPOaNxFrBRPR1dcUzuQDfKQXxp1P1AMBZ8jpZ2hmAsDGRrnEiUgdB04t89/1O/w1cDnyilFU="
USER_ID = "2006496715"

def send_line_message(message):
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

def is_day_before_holiday(date):
    weekday = date.weekday()
    return weekday == 5 or (weekday == 6 and date + timedelta(days=1) in holidays)

def check_availability():
    url = "https://www3.yadosys.com/reserve/ja/room/calendar/147/ehejfcebejdheigbgihfgpdn/all"

    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)  # ページの読み込みを待つ

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

    driver.quit()
    return available_dates

def main():
    available_dates = check_availability()
    if available_dates:
        message = "ほったらかしキャンプ場で以下の日に空きが出ました:\n" + "\n".join(available_dates)
        send_line_message(message)
    else:
        print("現在、空きはありません。")

if __name__ == "__main__":
    main()
