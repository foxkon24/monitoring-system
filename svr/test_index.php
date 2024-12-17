<!DOCTYPE html>
<html lang="ja">
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1, minimum-scale=1, shrink-to-fit=no, user-scalable=no">
    <link rel="stylesheet" href="css/style.css">
    <title>サーバー室温監視システム</title>
</head>
<body>
    <div class="layout">
        <header><h1>サーバー室温監視システム</h1></header>
        <nav>
            <ul>
                <li><a href="test_index.php">Top</a></li>
                <li><a href="test_view_graph.html">温度データ履歴</a></li>
            </ul>
        </nav>
        <div class="contents-grid">
            <div class="card1">
                <div class="card1-grid-container">
                    <div class="card1-grid-item1">温度</div>
                    <div class="card1-grid-item2"><?php echo do_get( 'temp' ); ?>℃</div>
                </div>
            </div>
            <div class="card2">
                <div class="card1-grid-container">
                    <div class="card2-grid-item1">測定日時</div>
                    <div class="card2-grid-item2"><?php echo do_get( 'date' ) . " " . do_get( 'time' ); ?></div>
                </div>
            </div>
        </div>
        <footer>&nbsp;&nbsp;Copyright&copy;&nbsp;&nbsp;2024&nbsp;&nbsp;株式会社&nbsp;共立電機製作所&nbsp;&nbsp;All&nbsp;rights&nbsp;reserved.</footer>
    </div>
</body>
</html>

<?php
    //レコード取得
    function do_get( $column ){
        require "db_connect.php";

        if( isset( $column ) ){
            try{
                // 最新レコードを取得するSQL文
                $sqlcmd = "SELECT * FROM test_rcd_temp ORDER BY date DESC, time DESC LIMIT 1";
                $result = $pdo->query( $sqlcmd );
                $row = $result->fetch( PDO::FETCH_ASSOC );

                if( isset( $row[ $column ] ) ){
                    return $row[ $column ];
                }
                else{
                    return null;
                }
            }
            catch( PDOException $ex ){
                echo "エラー: " . $ex->getMessage();

                return null;
            }
        }
        else{
            echo "パラメーター エラー";

            return null;
        }
    }
?>
