import mysql.connector


def get_latest_temp():
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'user',
        password = 'kyo_user_727880',
        database = 'temp_room_svr'
    )
    cursor = conn.cursor( dictionary = True )
    cursor.execute( 'SELECT * FROM test_rcd_temp ORDER BY date DESC, time DESC LIMIT 1' )
    latest_record = cursor.fetchone()
    cursor.close()
    conn.close()

    return latest_record


if __name__ == "__main__":
    latest_temp = get_latest_temp()

    if latest_temp:
        print( f"Date: { latest_temp['date'] }" )
        print( f"Time: { latest_temp['time'] }" )
        print( f"Temperature: { latest_temp['temp'] }" )
    else:
        print( "not record." );

