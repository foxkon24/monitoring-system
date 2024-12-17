<?php
$date = $_POST[ 'date' ];

require 'db_connect.php';

try {
    $stmt = $pdo->prepare( '
        SELECT
            date, time, temp
        FROM test_rcd_temp
        WHERE date = :date
    ' );
    $stmt->bindValue( ':date', $date );
    $stmt->execute();

    $data = [];
    while( $row = $stmt->fetch( PDO::FETCH_ASSOC ) ){
        $data[] = $row;
    }

    header( 'Content-Type: application/json' );
    echo json_encode( $data );
}
catch( PDOException $ex ){
    echo 'エラー: ' . $ex->getMessage();
}
