#!/usr/bin/python


import psycopg2
import os


def add_command(conn, server_id, command, message):
    """
    Adds a new command to the bot
    :param conn:
    :param server_id:
    :param command:
    :param message:
    :return:
    """
    cursor = conn.cursor()
    send_query(cursor, """
        SELECT * FROM COMMAND_LIST
        WHERE server_id = %s
            AND command_string = %s
            AND entry_value = %s;
            ;""",
               (server_id, command, message))
    if (cursor.rowcount > 0):
        print("That command already exists!\n", "Count=%d" % (cursor.rowcount))
        cursor.close()
        return False
    send_query(cursor, """ INSERT INTO COMMAND_LIST (server_id, command_string, entry_value) VALUES (%s,%s,%s)""",
               (server_id, command, message))
    cursor.close()
    conn.commit()
    return True


def remove_command(conn, server_id=None, command="", command_id=None):
    cursor = conn.cursor()
    query = ""
    params = None
    if (command_id):
        query = """
        DELETE FROM COMMAND_LIST
        WHERE command_id = %s;
        """
        params = (command_id,)
    else:
        query = """
        DELETE FROM COMMAND_LIST
        WHERE server_id = %s
            AND command_string = %s
        """
        params = (server_id, command)
    send_query(cursor, query, params)
    cursor.close()
    conn.commit()


def get_all_commands(conn, server_id):
    cursor = conn.cursor()
    send_query(cursor, """
        SELECT command_id,command_string,entry_value FROM COMMAND_LIST
        WHERE server_id=%s
        ORDER BY 
            command_string ASC,
            command_id ASC;
        
    """,
               (server_id,))
    results = None
    if cursor.rowcount > 0:
        results = cursor.fetchall()
    cursor.close()
    return results


def get_all_command_strings(conn, server_id):
    cursor = conn.cursor()
    send_query(cursor, """
        SELECT DISTINCT command_string FROM COMMAND_LIST
        WHERE server_id=%s
        ORDER BY
            command_string ASC;
    """, (server_id,))
    results = None
    if cursor.rowcount > 0:
        results = cursor.fetchall()
    cursor.close()
    return results


def get_all_responses_for_command(conn, server_id, command):
    cursor = conn.cursor()
    send_query(cursor, """
        SELECT command_id,command_string,entry_value FROM COMMAND_LIST
        WHERE server_id=%s
            AND command_string = %s
        ORDER BY 
            command_string ASC,
            command_id ASC; 
    """,
               (server_id, command))
    results = None
    if cursor.rowcount > 0:
        results = cursor.fetchall()
    return results


def add_server(conn, server_id, timeout):
    if get_server_timeout(conn, server_id) >= 0:
        return
    if timeout < 0:
        timeout = 30
    cursor = conn.cursor()
    send_query(cursor,
               """INSERT INTO SERVER_LIST (server_id, timeout_seconds) VALUES (%s, %s)""",
               (server_id, timeout))
    cursor.close()
    conn.commit()


def set_server_timeout(conn, server_id, timeout):
    # todo implement set_server_timeout
    cursor = conn.cursor()
    send_query(cursor,
               """
               UPDATE SERVER_LIST
               SET timeout_seconds = %s
               WHERE SERVER_LIST.server_id=%s;
               """, (timeout, server_id))
    return


def get_server_timeout(conn, server_id):
    cursor = conn.cursor()
    send_query(cursor, """
            SELECT timeout_seconds FROM SERVER_LIST WHERE SERVER_LIST.server_id=%s""", (server_id,))
    result = cursor.fetchone()
    cursor.close()
    if not result:
        return -1
    # print(result[0])
    return result[0]


def select_all(conn):
    cursor = conn.cursor()
    send_query(cursor, """
    SELECT * FROM COMMAND_LIST
    """)


def get_message(conn, server_id, command, to_search):
    """
    :param conn:
    :param server_id:
    :param command:
    :return:
    """
    cursor = conn.cursor()
    query = ""
    params = None
    if to_search:
        query = """
        SELECT entry_value
        FROM COMMAND_LIST
        WHERE server_id = %s
            AND command_string = %s
            AND entry_value LIKE %s
        ORDER BY RANDOM()
        LIMIT 1;
        """
        params = (server_id, command, "%%" + to_search + "%%")
    else:
        query = """
                SELECT entry_value
                FROM COMMAND_LIST
                WHERE server_id = %s
                    AND command_string = %s
                ORDER BY RANDOM()
                LIMIT 1;
                """
        params = (server_id, command)

    send_query(cursor, query, params)
    message = cursor.fetchone()
    cursor.close()
    if not message:
        return ""
    # print(message)
    return message[0]


def create_tables(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               CREATE TABLE SERVER_LIST (
                   server_id bigint PRIMARY KEY,
                   timeout_seconds int
               );
               CREATE TABLE COMMAND_LIST (
                   command_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                   server_id bigint,
                   command_string varchar(50) NOT NULL,
                   entry_value varchar(1000) NOT NULL
               );
               CREATE INDEX command_index
               ON COMMAND_LIST(server_id,command_string);
               """)
    cursor.close()
    conn.commit()


def add_timed_out_users_table(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               CREATE TABLE TIMED_OUT_USERS (
                   timed_out_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                   server_id bigint NOT NULL,
                   user_id bigint NOT NULL,
                   timeout_end bigint NOT NULL
               );
               """)
    cursor.close()
    conn.commit()
    return


def get_timeout_role_for_server(conn, server_id):
    cursor = conn.cursor()
    send_query(cursor,
               """
               SELECT timeout_role_id from SERVER_LIST
               WHERE server_id=%s;  
               """, (server_id,))
    if cursor.rowcount > 0:
        results = cursor.fetchone()
    cursor.close()
    return results[0]


def add_timeout_role_for_server(conn, server_id, role_id):
    cursor = conn.cursor()
    send_query(cursor,
               """
               UPDATE SERVER_LIST
               SET timeout_role_id=%s
               WHERE server_id=%s;  
               """, (role_id, server_id))
    cursor.close()
    conn.commit()


def add_timeout_role_column(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               ALTER TABLE SERVER_LIST
               ADD COLUMN timeout_role_id bigint;
               """)
    cursor.close()
    conn.commit()


def get_all_timeout_rows(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS;
               """)
    if cursor.rowcount > 0:
        results = cursor.fetchall()
    cursor.close()
    return results


def add_user_timeout_to_database(conn, server_id, user_id, until_time):
    cursor = conn.cursor()
    send_query(cursor,
               """
               INSERT INTO TIMED_OUT_USERS (server_id, user_id, timeout_end) VALUES (%s, %s, %s);
               """, (server_id, user_id, until_time))
    cursor.close()
    conn.commit()


def remove_user_timeout_from_database(conn, server_id, user_id):
    cursor = conn.cursor()
    send_query(cursor,
               """
               DELETE FROM TIMED_OUT_USERS
               WHERE server_id=%s
               AND user_id=%s;
               """, (server_id, user_id))
    cursor.close()
    conn.commit()


def get_user_timeouts_finished(conn, current_time):
    cursor = conn.cursor()
    send_query(cursor,
               """
               SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS
               WHERE timeout_end<=%s;
               """, (current_time,))
    if cursor.rowcount > 0:
        results = cursor.fetchall()
    cursor.close()
    return results


def drop_command_list(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               DROP TABLE IF EXISTS COMMAND_LIST CASCADE;
               """
               )
    cursor.close()
    conn.commit()


def drop_server_list(conn):
    cursor = conn.cursor()
    send_query(cursor,
               """
               DROP TABLE IF EXISTS SERVER_LIST CASCADE;
               """
               )
    cursor.close()
    conn.commit()


def send_query(cur, command, args=None):
    # print(command)
    try:
        if (args):
            cur.execute(command, args)
        else:
            cur.execute(command)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while executing command:\n", error)


def convert_from_map(conn, command_map, timeout):
    for server_id in timeout:
        add_server(conn, server_id, timeout[server_id])
        for command in command_map:
            for entry in command_map[command]:
                add_command(conn, server_id, command[1:], entry)
