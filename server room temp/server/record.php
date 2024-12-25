<?php
// データベース接続情報
$dsn = 'mysql:host=localhost;charset=utf8;dbname=temp_room_svr';
$user = 'user';
$password = 'kyo_user_727880';

// POSTされた日付を取得
$date = $_POST[ 'date' ];

// PDOを使用してデータベースに接続
try {
    $pdo = new PDO( $dsn, $user, $password );

    // SQL文を実行
    $stmt = $pdo->prepare( '
        SELECT
            date, time, temp
        FROM rcd_temp
        WHERE date = :date
    ' );
    $stmt->bindValue( ':date', $date );
    $stmt->execute();

    // 結果を配列に格納
    $data = [];
    while( $row = $stmt->fetch( PDO::FETCH_ASSOC ) ){
        $data[] = $row;
    }

    // JSON形式で出力
    header( 'Content-Type: application/json' );
    echo json_encode( $data );
}
catch( PDOException $ex ){
    echo 'エラー: ' . $ex->getMessage();
}
