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
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ApiException, TextMessage, PushMessageRequest

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")
URL = os.getenv("WEBSITE_URL")

def send_line_message(message):
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        try:
            line_bot_api.push_message(
                PushMessageRequest(
                    to=USER_ID,
                    messages=[TextMessage(text=message)]
                )
            )
            print("LINE通知を正常に送信しました。")
        except ApiException as e:
            print(f"LINE通知の送信に失敗しました: {e}")
            print(f"エラーの詳細: {e.body}")

def is_day_before_holiday(date):
    weekday = date.weekday()
    next_day = date + timedelta(days=1)
    return weekday == 5 or (weekday == 6 and jpholiday.is_holiday(next_day))

def check_availability():

    options = Options()
    #options.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendarTable"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        available_dates = []

        calendar_table = soup.find("table", class_="calendarTable")
        if calendar_table:
            rows = calendar_table.find_all("tr")[1:]
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
        print(f"An error occurred: {e}")
        return []
    finally:
        driver.quit()

def main():
    available_dates = check_availability()
    if available_dates:
        message = "ほったらかしキャンプ場で以下の日に空きが出ました:\n" + "\n".join(available_dates)
    else:
        message = "現在、ほったらかしキャンプ場に空き日時はありません。"
    
    send_line_message(message)

if __name__ == "__main__":
    main()