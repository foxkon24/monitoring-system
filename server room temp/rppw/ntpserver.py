"""
使い方

    import utime
    import ntpserver

    ntp = ntpserver.NtpServer()  #RTC設定
    ntp.setrtc()

    #現在日時取得
    def datetime_now():
        time_now = utime.localtime()
        sdate = "{:>4}".format(str(time_now[0])) + "/" + "{:0>2}".format(str(time_now[1])) + "/" + "{:0>2}".format(str(time_now[2]))
        stime = "{:>2}".format(str(time_now[3])) + ":" + "{:0>2}".format(str(time_now[4])) + ":" + "{:0>2}".format(str(time_now[5]))
        sdatetime = sdate + " " + stime

        return sdatetime

    str_datetime = datetime_now()
    print(f"日時: {str_datetime}")

"""

from micropython import const
import usocket as socket
try:
    import ustruct as struct
except:
    import struct
import machine
import utime


class NtpServer:
    #定数
    #NTPサーバー
    NTP_HOST = "ntp.nict.jp"
    #NTP_HOST = "time-c.nist.gov"
    #NTP_HOST = "time.cloudflare.com"
    #NTP_HOST = "time.google.com"

    NTP_PORT = const(123)

    JAPAN_TIME = const(9 * 60 * 60)
    TIMEOUT = const(2)


    #コンストラクタ
    def __init__(self):
        self.tm = []


    #NTPサーバー日時データ取得
    def getntpdatetime(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = const(0x1b)

        addr = socket.getaddrinfo(self.NTP_HOST, self.NTP_PORT)[0][-1]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.settimeout(TIMEOUT)
            res = sock.sendto(NTP_QUERY, addr)
            msg = sock.recv(48)
        finally:
            sock.close()

        val = struct.unpack("!I", msg[40:44])[0]

        EPOCH_YEAR = utime.gmtime(0)[0]
        if EPOCH_YEAR == const(2000):
            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24 * 60 * 60
            NTP_DELTA = 3155673600
        elif EPOCH_YEAR == const(1970):
            # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24 * 60 * 60
            NTP_DELTA = 2208988800
        else:
            raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

        return (val - NTP_DELTA)


    #日時設定
    def setrtc(self):
        t = self.getntpdatetime()

        if t >= 0:
            self.tm = utime.gmtime(t + JAPAN_TIME)

            #Raspberry Pi Pico WのRTCに設定
            machine.RTC().datetime((self.tm[0], self.tm[1], self.tm[2], self.tm[6] + 1, self.tm[3], self.tm[4], self.tm[5], 0))

            print("RTC OK.")

            return True
        else:
            print("RTC NG.")

            return False


