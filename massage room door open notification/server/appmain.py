import asyncio
import os
from datetime import datetime, timedelta
import aiohttp
import aiofiles

# ファイルパスとWebhook URLの設定
RECORD_FL_PATH = r'D:\xampp\htdocs\system\room_door\massage\record.txt'
WEBHOOK_URL = 'https://prod-08.japaneast.logic.azure.com:443/workflows/4f8619c2ae244bea87c153113ad053a8/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oVtYqDBQMA46Ly3SX1uoQCfOUlqi4BFkJ7zrGcKU2ew'

# 監視間隔を30分（1800秒）に設定
NOTIFICATION_INTERVAL = timedelta(minutes=30)

async def read_last_three_records(file_path):
    """ファイルから最後の3行のレコードを非同期で読み取る"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            lines = content.splitlines()
            last_three = lines[-3:] if len(lines) >= 3 else lines
            records = [line.strip().split(',') for line in last_three]
            door_states = [int(record[2]) for record in records]

            return door_states
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f'エラーが発生しました: {e}')
        return []

async def send_webhook_notification(session, url, message):
    """Webhookにメッセージを非同期で送信する"""
    try:
        payload = {
            'type': 'message',
            'attachments': [
                {
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'content': {
                        '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                        'type': 'AdaptiveCard',
                        'version': '1.4',
                        'body': [
                            {
                                'type': 'TextBlock',
                                'text': message['title'],
                                'size': 'ExtraLarge'
                            },
                            {
                                'type': 'ColumnSet',
                                'columns': [
                                    {
                                        'type': 'Column',
                                        'width': 'auto',
                                        'items': [
                                            {
                                                'type': 'TextBlock',
                                                'text': message['timestamp'],
                                                'size': 'Default'
                                            }
                                        ]
                                    },
                                    {
                                        'type': 'Column',
                                        'width': 'stretch',
                                        'items': [
                                            {
                                                'type': 'TextBlock',
                                                'text': message['message'],
                                                'size': 'Default'
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

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        async with session.post(url, headers=headers, json=payload) as response:
            # レスポンスの詳細を出力
            status_code = response.status
            response_text = await response.text()
            print(f'ステータスコード: {status_code}')
            print(f'レスポンス内容: {response_text}')

            # 202や200は成功とみなす
            if status_code in [200, 202]:
                print(f'Webhook通知が正常に送信されました（ステータスコード: {status_code}）')
                return True
            else:
                print(f'Webhook通知の送信に失敗しました。ステータスコード: {status_code}')
                return False

    except Exception as e:
        print(f'Webhook送信エラー: {e}')
        return False

async def main():
    last_notification_time = None
    last_notification_success = False
    last_size = os.path.getsize(RECORD_FL_PATH) if os.path.exists(RECORD_FL_PATH) else 0

    print('ファイル監視を開始しました...')

    # aiohttpのセッションを作成
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                current_size = os.path.getsize(RECORD_FL_PATH) if os.path.exists(RECORD_FL_PATH) else 0

                if current_size > last_size:
                    door_states = await read_last_three_records(RECORD_FL_PATH)

                    if len(door_states) == 3 and all(state == 1 for state in door_states):
                        current_time = datetime.now()

                        # 最後の通知から30分経過している、または前回の通知が失敗している場合
                        if (last_notification_time is None or (current_time - last_notification_time) >= NOTIFICATION_INTERVAL or not last_notification_success):
                            contents = {
                                'title': 'マッサージ室 ドア開閉通知',
                                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'message': 'マッサージ室のドアが開きました。'
                            }

                            # Webhook通知を送信し、結果を記録
                            last_notification_success = await send_webhook_notification(session, WEBHOOK_URL, contents)
                            if last_notification_success:
                                last_notification_time = current_time
                                print(f'次回の通知は {(current_time + NOTIFICATION_INTERVAL).strftime("%Y-%m-%d %H:%M:%S")} 以降に可能です')

                    last_size = current_size

                await asyncio.sleep(1)

            except Exception as e:
                print(f'エラーが発生しました: {e}')
                await asyncio.sleep(5)

if __name__ == '__main__':
    # イベントループを取得して非同期メインを実行
    asyncio.run(main())

