<?php
    // エラーレポート設定
    error_reporting(E_ALL);
    ini_set('display_errors', 1);

    // 現在の時刻を取得（日本のタイムゾーンに設定）
    date_default_timezone_set('Asia/Tokyo');
    $current_time = new DateTime();
    $current_hour = (int)$current_time->format('G'); // 24時間形式で時間を取得
    $current_day = (int)$current_time->format('w'); // 0（日曜）から6（土曜）

    // 水曜日(3)と木曜日(4)、および9:00-16:00の時間帯かチェック
    $is_allowed_day = in_array($current_day, [3, 4]); // 水曜日か木曜日
    $is_allowed_time = $current_hour >= 9 && $current_hour < 16; // 9:00-16:00

    // 許可された日時でない場合
    //if (!$is_allowed_day || !$is_allowed_time) {
    //    http_response_code(403);
    //    echo json_encode([
    //        'status' => 'error',
    //        'message' => '登録は水曜日・木曜日の9:00から16:00までの間のみ可能です。'
    //    ]);
    //    exit;
    //}

    // HTTPリクエストのContent-Typeヘッダーをチェック
    if ($_SERVER['CONTENT_TYPE'] !== 'application/json') {
        http_response_code(400);
        echo json_encode(['error' => 'Content-Type must be application/json']);
        exit;
    }

    // POSTデータを取得
    $json = stripslashes(file_get_contents('php://input'));
    $data = json_decode($json, true);

    // データのバリデーション
    if (!isset($data['date']) || !isset($data['time']) || !isset($data['doorstatus'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing required fields']);
        exit;
    }

    // CSVファイルのパス
    $csv_file = 'record_test.txt';

    // データの整形
    $door_status = $data['doorstatus'];
    $csv_line = sprintf("%s,%s,%d\n", $data['date'], $data['time'], $door_status);

    try {
        // ファイルの存在確認
        $file_exists = file_exists($csv_file);

        // ファイルが存在しない場合の処理
        if (!$file_exists) {
            // 新規ファイル作成モードでオープン
            $fp = fopen($csv_file, 'w');
            if (!$fp) {
                throw new Exception('Failed to create new file');
            }
            fclose($fp);

            // ファイル作成のログ
            error_log(date('Y-m-d H:i:s') . " - Created new file: " . $csv_file);
        }

        // 追記モードでファイルをオープン
        $fp = fopen($csv_file, 'a');
        if (!$fp) {
            throw new Exception('Failed to open file');
        }

        if (flock($fp, LOCK_EX)) {
            // データを書き込み
            if (fwrite($fp, $csv_line) === false) {
                throw new Exception('Failed to write data');
            }

            // ロックを解放
            flock($fp, LOCK_UN);
        }
        else {
            throw new Exception('Failed to lock file');
        }

        fclose($fp);

        // 成功レスポンス
        $response = [
            'status' => 'success',
            'message' => $file_exists ? 'Data recorded successfully' : 'New file created and data recorded successfully',
            'data' => [
                'date' => $data['date'],
                'time' => $data['time'],
                'door_status' => $door_status
            ]
        ];

        http_response_code(200);
        echo json_encode($response);
    }
    catch (Exception $e) {
        // エラー発生時
        if (isset($fp) && is_resource($fp)) {
            flock($fp, LOCK_UN);
            fclose($fp);
        }

        http_response_code(500);
        echo json_encode([
            'status' => 'error',
            'message' => $e->getMessage()
        ]);
    }
?>
