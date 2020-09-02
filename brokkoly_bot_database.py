#!/usr/bin/python


import psycopg2
import os


class BrokkolyBotDatabase():
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url, sslmode='require')

    def add_command(self, server_id, command, message):
        """
        Adds a new command to the bot
        :param conn:
        :param server_id:
        :param command:
        :param message:
        :return:
        """
        cursor = self.conn.cursor()
        self.send_query(cursor, """
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
        self.send_query(cursor,
                        """ INSERT INTO COMMAND_LIST (server_id, command_string, entry_value) VALUES (%s,%s,%s)""",
                        (server_id, command, message))
        cursor.close()
        self.conn.commit()
        return True

    def remove_command(self, server_id=None, command="", command_id=None):
        cursor = self.conn.cursor()
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
        self.send_query(cursor, query, params)
        cursor.close()
        self.conn.commit()

    def get_all_commands(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
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

    def get_all_command_strings(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
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

    def get_all_responses_for_command(self, server_id, command):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
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

    def add_server(self, server_id, cooldown):
        # todo not sure about this
        if self.get_server_cooldown(server_id) >= 0:
            return
        if cooldown < 0:
            cooldown = 30
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """INSERT INTO SERVER_LIST (server_id, timeout_seconds) VALUES (%s, %s)""",
                        (server_id, cooldown))
        cursor.close()
        self.conn.commit()

    def get_all_servers(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id FROM SERVER_LIST;
                        """)
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def set_server_details(self, server_id, server_name="", server_url=""):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        UPDATE SERVER_LIST
                        SET name = %s,
                            icon_url_64 = %s
                        WHERE server_id = %s;
                        """, (server_name, server_url, server_id))
        cursor.close()
        self.conn.commit()

    def set_server_cooldown(self, server_id, cooldown):
        # todo implement set_server_timeout
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        UPDATE SERVER_LIST
                        SET timeout_seconds = %s
                        WHERE SERVER_LIST.server_id=%s;
                        """, (cooldown, server_id))
        cursor.close()
        self.conn.commit()
        return

    def get_server_cooldown(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                SELECT timeout_seconds FROM SERVER_LIST WHERE SERVER_LIST.server_id=%s""", (server_id,))
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return -1
        # print(result[0])
        return result[0]

    def select_all(self):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
        SELECT * FROM COMMAND_LIST
        """)

    def get_message(self, server_id, command, to_search):
        """
        :param conn:
        :param server_id:
        :param command:
        :return:
        """
        cursor = self.conn.cursor()
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
                    WHERE server_id=%s
                        AND command_string=%s
                    ORDER BY RANDOM()
                    LIMIT 1;
                    """
            params = (server_id, command)

        self.send_query(cursor, query, params)
        message = cursor.fetchone()
        cursor.close()
        if not message:
            return ""
        # print(message)
        return message[0]

    def create_tables(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
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
                        
                        CREATE TABLE TIMED_OUT_USERS (
                            timed_out_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            server_id bigint NOT NULL,
                            user_id bigint NOT NULL,
                            timeout_end bigint NOT NULL
                        );
                        """)
        cursor.close()
        self.conn.commit()

    def add_timed_out_users_table(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        CREATE TABLE TIMED_OUT_USERS (
                            timed_out_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            server_id bigint NOT NULL,
                            user_id bigint NOT NULL,
                            timeout_end bigint NOT NULL
                        );
                        """)
        cursor.close()
        self.conn.commit()
        return

    def add_server_details_columns(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        ALTER TABLE SERVER_LIST
                        ADD COLUMN icon_url_64 VARCHAR(500),
                        ADD COLUMN name VARCHAR(1000);
                        """)
        cursor.close()

    def get_timeout_role_for_server(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT timeout_role_id from SERVER_LIST
                        WHERE server_id=%s;  
                        """, (server_id,))
        if cursor.rowcount > 0:
            results = cursor.fetchone()
        cursor.close()
        return results[0]

    def add_timeout_role_for_server(self, server_id, role_id):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        UPDATE SERVER_LIST
                        SET timeout_role_id=%s
                        WHERE server_id=%s;  
                        """, (role_id, server_id))
        cursor.close()
        self.conn.commit()

    def add_timeout_role_column(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        ALTER TABLE SERVER_LIST
                        ADD COLUMN timeout_role_id bigint;
                        """)
        cursor.close()
        self.conn.commit()

    def get_all_timeout_rows(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS;
                        """)
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def add_user_timeout_to_database(self, server_id, user_id, until_time):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        INSERT INTO TIMED_OUT_USERS (server_id, user_id, timeout_end) VALUES (%s, %s, %s);
                        """, (server_id, user_id, until_time))
        cursor.close()
        self.conn.commit()

    def remove_user_timeout_from_database(self, server_id, user_id):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DELETE FROM TIMED_OUT_USERS
                        WHERE server_id=%s
                        AND user_id=%s;
                        """, (server_id, user_id))
        cursor.close()
        self.conn.commit()

    def get_user_timeouts_finished(self, current_time):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS
                        WHERE timeout_end<=%s;
                        """, (current_time,))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def drop_command_list(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DROP TABLE IF EXISTS COMMAND_LIST CASCADE;
                        """
                        )
        cursor.close()
        self.conn.commit()

    def drop_server_list(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DROP TABLE IF EXISTS SERVER_LIST CASCADE;
                        """
                        )
        cursor.close()
        self.conn.commit()

    def send_query(self, cur, command, args=None):
        # print(command)
        try:
            if (args):
                cur.execute(command, args)
            else:
                cur.execute(command)

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while executing command:\n", error)

    # def convert_from_map(self, command_map, timeout):
    #     for server_id in timeout:
    #         add_server(conn, server_id, timeout[server_id])
    #         for command in command_map:
    #             for entry in command_map[command]:
    #                 add_command(conn, server_id, command[1:], entry)
