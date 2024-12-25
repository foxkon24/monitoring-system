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
SVR_URL = "http://172.16.20.250/system/temp/room_svr/test_regist.php"  #"http://172.16.20.250/system/temp/room_svr/regist.php"

WAIT_TIME_TASK = const( 3 )


#変数
sens_res = 0
cnt = 0


#現在日時取得
#日付フォーマットは、「yyyy-MM-dd」形式とする。
def datetime_now():
    time_now = utime.localtime()
    sdate = "{:>4}".format( str( time_now[ 0 ] ) ) + "-" + "{:0>2}".format( str( time_now[ 1 ] ) ) + "-" + "{:0>2}".format( str( time_now[ 2 ] ) )
    stime = "{:>2}".format( str( time_now[ 3 ] ) ) + ":" + "{:0>2}".format( str( time_now[ 4 ] ) ) + ":" + "{:0>2}".format( str( time_now[ 5 ] ) )
    sdatetime = sdate + " " + stime

    print( f"日時: {sdatetime}" )

    return ( sdate, stime )


#リードセンサー状態取得
def get_reed_sens():
    global reed

    res = reed.value()
    if res == 1:  #On(センサー接触)
        print("リードセンサー状態: On")
    else:  #Off(センサー非接触)
        print("リードセンサー状態: Off")

    return ( res )


#POST通信
def do_post( date, time, temperature ):
    headers = { "Content-Type": "application/json" }

    body = { "date": date, "time": time, "temperature": temperature }
    resp = urequests.post( SVR_URL, headers = headers, data = ujson.dumps( body ).encode( "utf-8" ) )

    print( "HTTP Status Code:", resp.status_code )
    print( resp.text )

    resp.close()


#タスク処理
async def do_task():
    global sens_res

    print( "start task..." )

    while True:
        dt, tm = datetime_now()

        sens_res = get_reed_sens()
        if sens_res == 1:  #本来Onだが、ここでは、Offと判定
            print("Door: Open.")
        else:  #本来Offだが、ここでは、Onと判定
            print("Door: Close.")

        await uasyncio.sleep( WAIT_TIME_TASK )


#メイン処理
if __name__ == "__main__":
    #初期化
    try:
        lcl_led = Pin( "LED", Pin.OUT )
        reed = Pin(14, Pin.IN)
    except Exception as e:
        print( "device init - Exception Error: ", e )

    nw = wificonnect.WiFiConnect()
    if nw.connect():  #Wi-Fi接続
        lcl_led.on()

        retry_n = 3
        rtc = ntpserver.NtpServer()  #RTC設定
        for n in range( retry_n ):
            if rtc.setrtc() != False:
                break

            print( "Waiting RTC Set..." )

        else:
            print( "RTC Set Error." )
            machine.reset()

        loop = uasyncio.new_event_loop()
        loop.create_task( do_task() )

        try:
            loop.run_forever()

        except Exception as ex:
            print( "Exception Error: ", ex )

        except KeyboardInterrupt:
            print( "Program Interrupted by the user." )
            pass

        finally:
            loop.close()

            lcl_led.off()

            machine.reset()

    else:  #Wi-Fi接続失敗
        while True:  #LED点滅
            lcl_led.toggle()
            utime.sleep( 2.5 )


