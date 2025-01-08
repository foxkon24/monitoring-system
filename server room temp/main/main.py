from micropython import const
from machine import Pin, I2C
import utime
import ahtx0
from i2c_config import *
from ssid_config import *
import wificonnect
import ntpserver
import umail
from mail_config import *
import urequests
import ujson
import uasyncio


#定数
SVR_URL = "http://172.16.20.250/system/temp/room_svr/regist.php"

WAIT_TIME_TASK = const(60)
TEMP_ABNORMAL = float(25.0)  #異常温度(℃)
CNT_OVERFLOW = 10


#変数
temp = float(0.0)
cnt = 0


#現在日時取得
#日付フォーマットは、「yyyy-MM-dd」形式とする。
def datetime_now():
    time_now = utime.localtime()
    sdate = "{:>4}".format(str(time_now[0])) + "-" + "{:0>2}".format(str(time_now[1])) + "-" + "{:0>2}".format(str(time_now[2]))
    stime = "{:>2}".format(str(time_now[3])) + ":" + "{:0>2}".format(str(time_now[4])) + ":" + "{:0>2}".format(str(time_now[5]))
    sdatetime = sdate + " " + stime

    print(f"日時: {sdatetime}")

    return (sdate, stime)


#温度取得
def get_temp():
    global sensor
    global temp

    temp = round(sensor.temperature, 1)

    print(f"温度: {str(temp)}℃")

    return temp


#メール送信処理
def sent_mail(host, port, from_addr, from_pwd, to_addr, subject, body_text):
    if (re.search("outlook", from_addr)) or (re.search("hotmail", from_addr)):  #outlook系の場合
        smtp = umail.SMTP(host, port)
    else:  #gmailの場合
        smtp = umail.SMTP(host, port, sslflg = True)

    smtp.login(from_addr, from_pwd)  #ログイン(アプリパスワード)
    smtp.to(to_addr, mail_from = from_addr)  #送信先
    smtp.write("To:" + to_addr + "\n")  #送信先
    smtp.write("Subject:" + subject + "\n")  #題名
    smtp.write("\n")  #ヘッダー部と本文を分けるために必要
    smtp.write(body_text)  #本文
    smtp.send()
    smtp.quit()

    print("E-mail Sent.")


#メール通知
def mail_notify(temp, multiple_sent_enable = False):
    email_subject = "サーバー室温監視システム通知"
    body_text = f"サーバー室温が{str(temp)}℃以上になっています。\nサーバー室を確認してください。"

    sent_mail(mail_config["smtp_server"], mail_config["smtp_port"], mail_config["from_email"], mail_config["from_app_pwd"], mail_config["to_email_1"], email_subject, body_text)

    if multiple_sent_enable != False:
        sent_mail(mail_config["smtp_server"], mail_config["smtp_port"], mail_config["from_email"], mail_config["from_app_pwd"], mail_config["to_email_2"], email_subject, body_text)


#POST通信
def do_post(date, time, temperature):
    headers = { "Content-Type": "application/json" }

    body = { "date": date, "time": time, "temperature": temperature }
    resp = urequests.post(SVR_URL, headers = headers, data = ujson.dumps(body).encode("utf-8"))

    print("HTTP Status Code:", resp.status_code)
    print(resp.text)

    resp.close()


#タスク処理
async def do_task():
    global temp
    global cnt

    print("start task...")

    while True:
        dt, tm = datetime_now()

        temp = get_temp()

        #for test
        #do_post(dt, tm, temp)

        #if temp >= TEMP_ABNORMAL:  #異常温度以上
        #    mail_notify(temp, multiple_sent_enable = True)

        if cnt >= CNT_OVERFLOW:
            cnt = 0

            do_post(dt, tm, temp)

            if temp >= TEMP_ABNORMAL:  #異常温度以上
                mail_notify(temp, multiple_sent_enable = True)

        else:
            cnt += 1

            print(f"cnt= {str(cnt)}")

        await uasyncio.sleep(WAIT_TIME_TASK)


#メイン処理
if __name__ == "__main__":
    try:
        lcl_led = Pin("LED", Pin.OUT)

        i2c = I2C(i2c_config["index"], scl = Pin(i2c_config["scl"]), sda = Pin(i2c_config["sda"]))
        sensor = ahtx0.AHT10(i2c)  #温湿度センサー(AHT21B)

        nw = wificonnect.WiFiConnect()
        if nw.connect():  #Wi-Fi接続
            lcl_led.on()

            retry_n = 3
            rtc = ntpserver.NtpServer()  #RTC設定
            for n in range(retry_n):
                if rtc.setrtc() != False:
                    break

                print("Waiting RTC Set...")
            else:
                print("RTC Set Error.")
                machine.reset()

            loop = uasyncio.new_event_loop()
            loop.create_task(do_task())

            try:
                loop.run_forever()
            except Exception as ex:
                print("Exception Error: ", ex)
            except KeyboardInterrupt:
                print("Program Interrupted by the user.")
                pass
            finally:
                loop.close()
                lcl_led.off()

                machine.reset()

        else:  #Wi-Fi接続失敗
            while True:  #LED点滅
                lcl_led.toggle()
                utime.sleep(1)

    except Exception as e:
        print("device init - Exception Error: ", e)

        while True:  #LED点滅
            lcl_led.toggle()
            utime.sleep(2.5)

