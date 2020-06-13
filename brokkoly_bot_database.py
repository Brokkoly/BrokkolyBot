#!/usr/bin/python


import psycopg2
import os


def add_command(conn, server_id, command, message):
    """

    :param conn:
    :param server_id:
    :param command:
    :param message:
    :return:
    """
    # TODO check if the entry already exists
    send_query(conn, """
    INSERT INTO COMMAND_LIST(server_id,command_string,entry_value)
    VALUES
        (%d,\'%s\',\'%s\');
    """ % (server_id, command, message)
               )
    return


def select_all(conn):
    send_query(conn, """
    SELECT * FROM COMMAND_LIST
    """)


def get_message(conn, server_id, command):
    """
    :param conn:
    :param server_id:
    :param command:
    :return:
    """

    message = send_query(conn, """
    SELECT entry_value
    FROM COMMAND_LIST
    WHERE server_id = %d
        AND command_string = \'%s\'
    ORDER BY RANDOM()
    LIMIT 1;
    """ % (server_id, command))
    return message


def create_tables(conn):
    send_query(conn,
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
    conn.commit()


def drop_command_list(conn):
    send_query(conn,
               """
               DROP TABLE IF EXISTS COMMAND_LIST CASCADE;
               """
               )


def drop_server_list(conn):
    send_query(conn,
               """
               DROP TABLE IF EXISTS SERVER_LIST CASCADE;
               """
               )


def send_query(conn, command):
    print(command)
    cur = conn.cursor()
    try:
        message = cur.execute(command)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while executing command:\n", error)
        message = ""
    finally:
        if (cur):
            cur.close()
        return message
