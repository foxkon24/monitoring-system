<?php

  $dsn = 'mysql:host=localhost;charset=utf8mb4;dbname=temp_room_svr';
  $user = 'user';
  $pwd = 'kyo_user_727880';

  try{
    $pdo = new PDO( $dsn, $user, $pwd );

    $pdo->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION );
    $pdo->setAttribute( PDO::ATTR_EMULATE_PREPARES, false );
  }
  catch( PDOException $ex ){
    print( "接続失敗: " . $ex->getMessage() );

    exit();
  }

?>
