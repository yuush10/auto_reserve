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
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ApiException, TextMessage, PushMessageRequest

load_dotenv()

#環境編集の取得と確認
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")
URL = os.getenv("WEBSITE_URL")

if not CHANNEL_ACCESS_TOKEN or not USER_ID or not URL:
    raise ValueError("必要な環境変数が設定されていません。")

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
    weekday = date.weekday() #曜日を取得。土曜日は5、日曜日は6
    next_day = date + timedelta(days=1) #翌日の日付を計算
    return weekday == 5 or (weekday == 6 and jpholiday.is_holiday(next_day)) #土曜日の場合、または日曜日でかつ翌日が祝日の場合にTrueを返す

def check_availability():

    options = Options() #Seleniumのオプションを設定するためのオブジェクトを作成
    options.add_argument("--headless=new") #ヘッドレスモードを使用する場合
    try: 
        #ChromeDriverをインストールし、指定したオプションでWebDriverを初期化
        print("ChromeDriverを初期化中...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 指定したURLにアクセス
        print("URLにアクセス中...")
        driver.get(URL)

        # 指定した要素（カレンダーテーブル）がページに表示されるまで最大10秒待機
        print("カレンダーテーブルを待機中...")
        try:
            WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/form/div[3]/div")) 
        )
        except TimeoutException:
            print("カレンダーテーブルが見つかりませんでした。")

        # ページのHTMLソースを取得
        print("ページのHTMLソースを取得中...")
        html = driver.page_source

        # BeautifulSoupを使ってHTMLを解析するためのオブジェクトを作成
        print("BeautifulSoupを使ってHTMLを解析するためのオブジェクトを作成中...")
        soup = BeautifulSoup(html, "html.parser")

        #予約可能な日付を格納するリスト
        print("予約可能な日付を確認中...")
        available_dates = []

        #BeautifulSoupオブジェクトからカレンダーのテーブルを取得
        print("BeautifulSoupオブジェクトからカレンダーのテーブルを取得中...")
        calendar_tables = soup.find_all("table")

        # テーブルの数をカウント
        table_count = len(calendar_tables)
        print(f"見つかったテーブルの数: {table_count}")

        for index, calendar_table in enumerate(calendar_tables):
            if calendar_table:
                # 年と月を取得するためのXPATH指定
                year_month_xpath = f'//*[@id="main"]/div[2]/div[{index + 1}]/h4'  # 年月情報が含まれる要素（XPATH）

                # Seleniumで年と月を取得
                year_month_element = driver.find_element(By.XPATH, year_month_xpath)
                year_month_text = year_month_element.text.strip()  # 年と月のテキストを取得

                # 年と月がくっついているため、年月を分離する処理を追加
                year = int(year_month_text[:4])  # 最初の4文字を年として取得
                month_text = year_month_text[4:].replace("月", "").strip()  #「月」を取り除いて残りを取得
                month = int(month_text) # 月が1桁の場合も考慮して整数に変換

                print(f"{year}年{month}月の日付を確認中…")  # 年と月を表示

                rows = calendar_table.find_all("tr")[1:] #ヘッダー行を除外                
                
                for row in rows:
                    cells = row.find_all("td") #すべての日付を取得
                    for cell in cells:
                        try: 
                            date_str_element = cell.find("span", class_="arial")  # <span class="arial">内の日付を取得
                            if date_str_element:  # 要素が存在する場合
                                date_str = date_str_element.text.strip()
                                if date_str:
                                    if date_str:
                                        #日付のパース
                                        date = datetime(year, month, int(date_str))  # 年、月、日で日付オブジェクトを作成
                                        # 空き状況の確認: "▲"または"◯"が含まれている場合
                                        if ("▲" in cell.text or "◯" in cell.text) and is_day_before_holiday(date):
                                            available_dates.append(date.strftime("%Y-%m-%d"))  # 空いている日付を追加
                        except Exception as e:
                            print(f"エラー発生: {e}")
                            print(f"行の内容: {row}")
                            print(f"セルの内容: {cell}")
            else:
                print("カレンダーのテーブルが見つかりませんでした。")
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
    else:
        message = "現在、ほったらかしキャンプ場に空き日時はありません。"
    
    print(message)
    send_line_message(message)

if __name__ == "__main__":
    main()