import time
import csv
import requests
import os
from datetime import datetime, timedelta  # timedeltaを追加

# ファイルパスとWebhook URLの設定
RECORD_FL_PATH = r"D:\xampp\htdocs\system\room_door\massage\record.txt"
WEBHOOK_URL = "https://prod-08.japaneast.logic.azure.com:443/workflows/4f8619c2ae244bea87c153113ad053a8/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oVtYqDBQMA46Ly3SX1uoQCfOUlqi4BFkJ7zrGcKU2ew"

# 監視間隔を30分（1800秒）に設定
NOTIFICATION_INTERVAL = timedelta(minutes=30)

def read_last_three_records(file_path):
    """ファイルから最後の3行のレコードを読み取る"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            last_three = lines[-3:] if len(lines) >= 3 else lines
            records = [line.strip().split(',') for line in last_three]
            door_states = [int(record[2]) for record in records]

            return door_states
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []

def send_webhook_notification(webhook_url, message):
    """Webhookにメッセージを送信する"""
    try:
        # メッセージの形式を、Microsoft Teamsのアダプティブカード形式に修正
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": message["title"],
                                "size": "ExtraLarge"
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": message["timestamp"],
                                                "size": "Default"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": message["message"],
                                                "size": "Default"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

        # ヘッダーを追加
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # POST要求を送信
        response = requests.post(webhook_url, headers=headers, json=payload)

        # レスポンスの詳細を出力
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス内容: {response.text}")

        # 202や200は成功とみなす
        if response.status_code in [200, 202]:
            print(f"Webhook通知が正常に送信されました（ステータスコード: {response.status_code}）")
            return True
        else:
            print(f"Webhook通知の送信に失敗しました。ステータスコード: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Webhook送信エラー: {e}")
        return False

def main():
    last_notification_time = None
    last_notification_success = False  # 最後の通知が成功したかを記録

    print("ファイル監視を開始しました...")

    last_size = os.path.getsize(RECORD_FL_PATH) if os.path.exists(RECORD_FL_PATH) else 0

    while True:
        try:
            current_size = os.path.getsize(RECORD_FL_PATH) if os.path.exists(RECORD_FL_PATH) else 0

            if current_size > last_size:
                door_states = read_last_three_records(RECORD_FL_PATH)

                if len(door_states) == 3 and all(state == 1 for state in door_states):
                    current_time = datetime.now()

                    # 最後の通知から1分経過している、または前回の通知が失敗している場合
                    if (last_notification_time is None or (current_time - last_notification_time) >= NOTIFICATION_INTERVAL or not last_notification_success):
                        # 現在の時刻を含めたメッセージを作成
                        contents = {
                            "title": "マッサージ室 ドア開閉通知",
                            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "message": "マッサージ室のドアが開きました。"
                        }

                        # Webhook通知を送信し、結果を記録
                        last_notification_success = send_webhook_notification(WEBHOOK_URL, contents)
                        if last_notification_success:
                            last_notification_time = current_time
                            print(f"次回の通知は {(current_time + NOTIFICATION_INTERVAL).strftime('%Y-%m-%d %H:%M:%S')} 以降に可能です")

                last_size = current_size

            time.sleep(1)

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

