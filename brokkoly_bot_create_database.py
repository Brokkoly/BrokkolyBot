import psycopg2
from psycopg2 import Error
from brokkoly_bot_database import *
import tokens

try:
    conn = psycopg2.connect(tokens.DATABASE_URL, sslmode='require')
except:
    print("Connection Failed")
    quit()

try:

    # drop_server_list(conn)
    # drop_command_list(conn)
    # create_tables(conn)

    add_command(conn, 0, "test", "test message")
    print(select_all(conn))
    print("Found Message: ", get_message(conn, 0, "test"))

    conn.commit()

    # cur = conn.cursor()
    # rows = cur.fetchall()
    # for row in rows:
    #     print
    #     "   ", row[1][1]
    # cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print("Error while accessing table", error)

finally:
    if (conn):
        conn.close()
        print("PostgreSCQL connection is closed")
