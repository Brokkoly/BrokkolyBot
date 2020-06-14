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
    cursor = None

    # drop_server_list(conn)
    # drop_command_list(conn)
    # create_tables(conn)

    # add_command(conn, 0, "test", "test message")

    insert_query = """ INSERT INTO COMMAND_LIST (server_id, command_string, entry_value) VALUES (%s,%s,%s)"""
    values = (0, "test", "test message")
    add_command(conn, 0, 'test', 'test_message')
    # cursor = conn.cursor()

    # cursor.execute(insert_query,values)
    conn.commit()

    # count = cursor.rowcount

    # print(count, "Record successfully inserted")
    # print(select_all(conn))
    print("Found Message: ", get_message(conn, 0, "test"))
    # select_query = "SELECT * FROM COMMAND_LIST"
    # cursor.execute(select_query)

    # rows = cursor.fetchall()
    # for row in rows:
    # print("Col0 = ",row[0])
    # print("Col1 = ", row[1])
    # print("Col2 = ", row[2])
    # print("Col3 = ", row[3], "\n")
    # cursor.close()
except (Exception, psycopg2.DatabaseError) as error:
    print("Error while accessing table", error)

finally:
    if (conn):
        if (cursor):
            cursor.close()
        conn.close()
        print("PostgreSCQL connection is closed")
