from micropython import const
from machine import Pin
import utime
from ssid_config import *
import wificonnect
import ntpserver
import urequests
import ujson
import uasyncio


#定数
SVR_URL = "http://172.16.20.250/system/room_door/massage/test_regist.php"  #"http://172.16.20.250/system/room_door/massage/regist.php"

WAIT_TIME_TASK = const(1)


#変数
door_status = 0
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


#リードセンサー状態取得
def get_reed_sens():
    global reed

    res = reed.value()
    if res == 1:  #On(センサー接触)
        print("リードセンサー状態: On")
    else:  #Off(センサー非接触)
        print("リードセンサー状態: Off")

    return (res)


#有効時間チェック
def is_allowed_time():
    """ 水曜日・木曜日の9:00-16:00の間のみTrueを返す """
    time_now = utime.localtime()
    weekday = time_now[6]  # 0=月曜日, 1=火曜日, ..., 6=日曜日
    hour = time_now[3]

    # 水曜日(2)または木曜日(3)かつ9時から16時の間
    return (weekday in [2, 3]) and (9 <= hour < 16)


#POST通信
def do_post(date, time, door_sts):
    if not is_allowed_time():
        print("現在は通信可能な時間帯ではありません")
        return

    headers = {"Content-Type": "application/json"}

    try:
        body = {"date": date, "time": time, "doorstatus": door_sts}
        resp = urequests.post(SVR_URL, headers=headers, data=ujson.dumps(body).encode("utf-8"))

        print("HTTP Status Code:", resp.status_code)
        print(resp.text)

        resp.close()
    except Exception as e:
        print("POST通信エラー:", e)


#タスク処理
async def do_task():
    global door_status

    print("start task...")

    while True:
        dt, tm = datetime_now()

        tmp = get_reed_sens()
        if tmp == 1:  #リードセンサーOn
            door_status = 0  #ドアクローズとする
            print("Door: Close.")
        else:  #リードセンサーOff
            door_status = 1  #ドアオープンとする
            print("Door: Open.")

        do_post(dt, tm, door_status)

        await uasyncio.sleep(WAIT_TIME_TASK)


#メイン処理
if __name__ == "__main__":
    #初期化
    try:
        lcl_led = Pin("LED", Pin.OUT)

        reed = Pin(14, Pin.IN)

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
                utime.sleep(2.5)

    except Exception as e:
        print("device init - Exception Error: ", e)

