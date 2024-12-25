from micropython import const
import network
import utime
import ubinascii
from ssid_config import *


class WiFiConnect:
    #定数
    WAIT_TIMEOUT = const(10)


    #コンストラクタ
    def __init__(self):
        self._wlan = None


    #接続待ち
    def wait_connection( self, tmout ):
        ret = True

        if tmout > 0:
            for n in range( tmout ):
                if ( self._wlan.status() < 0 )  or ( self._wlan.status() >= 3 ):
                    break

                print( "Waiting for connection..." )

                utime.sleep( 1 )

            else:  #カウントアップ
                ret = False

        else:  #パラメーターエラー
            ret = False

        return ret


    #接続
    def connect(self, ssid = ssid_config["ssid"], pwd = ssid_config["pwd"], ipaddr = None):
        ret = False

        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(True)
        self._wlan.connect(ssid, pwd)

        if self.wait_connection(tmout = WAIT_TIMEOUT):
            if self._wlan.status() != 3:
                print("Wi-Fi connection failed.")
            else:
                print("Wi-Fi connected.")

                status = self._wlan.ifconfig()

                if ipaddr != None:  #固定IPアドレス指定あり
                    self._wlan.ifconfig((ipaddr, status[1], status[2], status[3]))

                status = self._wlan.ifconfig()

                macaddr = str(ubinascii.hexlify(self._wlan.config("mac")))  #MACアドレス取得

                print(f"IPAddress: {status[0]}, Subnetmask: {status[1]}, Gateway: {status[2]}, DNS: {status[3]}, MACAddress: {macaddr}")

                ret = True

        else:  #タイムアウト
            print("Wi-Fi connection timed out.")

        return ret


