                    import pandas as pd
                    import matplotlib.pyplot as plt
                    from matplotlib import pyplot
                    from sqlalchemy import create_engine

                    engine = create_engine( 'mysql+pymysql://user:kyo_user_727880@172.16.20.250/temp_room_svr' )

                    date = Element( 'date' ).element.value

                    with engine.connect() as conn:
                        sql = f"""
                            SELECT date, time, temp
                            FROM test_rcd_temp
                            WHERE date = '{date}';
                            """
                        df = pd.read_sql( sql, conn )

                    plt.figure( figsize = ( 10, 5 ) )
                    plt.plot( df['datetime'], df['temp'] )
                    plt.xlabel( 'éûçè' )
                    plt.ylabel( 'â∑ìx' )
                    plt.title( f'{date}ÇÃâ∑ìxïœâª' )
                    plt.grid( True )

                    plt.savefig( 'plot.png' )
                    img_tag = Element( 'img', src='plot.png' )
                    plot_div = Element( 'div', id='plot' )
                    plot_div.element.append( img_tag )
