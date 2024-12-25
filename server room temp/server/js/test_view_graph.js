const ctx = document.getElementById( 'myChart' ).getContext( '2d' );

// フォーム送信時にグラフを描画
document.querySelector( 'form' ).addEventListener( 'submit', ( event ) => {
    event.preventDefault(); // フォームのデフォルト動作をキャンセル

    // fetchでデータを取得
    fetch( 'test_view_graph.php', {
        method: 'POST',
        body: new URLSearchParams( { date: document.getElementById( 'date' ).value } )
    })
    .then( response => response.json() )
    .then( data => {
        const labels = data.map( item => item.time );
        const temps = data.map( item => item.temp );

        // グラフを描画
        new Chart( ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '温度',
                    data: temps,
                    borderColor: 'blue',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '時刻'
                        }
                    },
                    y: {
                        ticks: {
                            stepSize: 0.05,
                        },
                        title: {
                            display: true,
                            text: '温度(℃)'
                        }
                    }
                }
            }
        });
    });
});
