<!DOCTYPE html>
<html lang="ja">
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1, minimum-scale=1, shrink-to-fit=no, user-scalable=no">
    <title>サーバー室温監視システム</title>
</head>
<body>
    <div>
        <?php
            $in_dat = json_decode( stripslashes( file_get_contents( "php://input" ) ), true );

            do_regist( $in_dat[ "date" ], $in_dat[ "time" ], $in_dat[ "temperature" ] );
        ?>
    </div>
</body>
</html>


<?php
    //DB登録
    function do_regist( $dt, $tm, $tmp ){
        require 'db_connect.php';

        if( ( isset( $dt ) ) && ( isset( $tm ) ) && ( isset( $tmp ) ) ){
            try{
                $sqlcmd = "INSERT INTO test_rcd_temp ( date, time, temp ) VALUES ( '" . $dt . "', '" . $tm . "', '" . $tmp . "' )";
                $result = $pdo->query( $sqlcmd );
                $pdo = null;

                header( "HTTP/1.0 201 Created" );

                echo "DB登録 成功";
            }
            catch( PDOException $ex ){
                echo "DB登録 エラー： " . $ex->getMessage();
            }
        }
        else{
            echo "パラメーター エラー";
        }
    }
?>
