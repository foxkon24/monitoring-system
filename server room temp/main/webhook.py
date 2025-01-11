from micropython import const
import urequests
import ujson


class Webhook:
    #webhook送信
    def send_webhook(self, url, payload):
        ret = False

        try:
            # HTTPヘッダーの設定
            headers = {
                'Content-Type': 'application/json'
            }

            # POSTリクエストを送信
            resp = urequests.post(url, headers=headers, data=ujson.dumps(payload).encode('utf-8'))

            print('Webhook応答結果:', resp.text)
            resp.close()

            ret = True
        except Exception as e:
            print('Webhook送信エラー:', str(e))

        return ret


    #webhook送信
    def send_webhook_msteams(self, url, payload):
        ret = False

        try:
            # HTTPヘッダーの設定
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # POSTリクエストを送信
            resp = urequests.post(url, headers=headers, data=ujson.dumps(payload).encode('utf-8'))

            print('Webhook応答結果:', resp.text)
            resp.close()

            ret = True
        except Exception as e:
            print('Webhook送信エラー:', str(e))

        return ret

